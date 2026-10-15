#!/usr/bin/env python3
"""Small, auditable research-brief CLI; Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass, asdict

MAX_FILE = 100_000
MAX_CORPUS = 500_000
HEADINGS = ('Snapshot', 'Bull case', 'Bear case', 'Open questions')
REVIEWS = {
    'balanced': 'Give the strongest supported positives and negatives equal consideration. Separate management expectations from reported results.',
    'conservative': 'Prioritize official reported results. Treat guidance and capacity benefits as conditional, and emphasize cash conversion and financial obligations.',
    'skeptical': 'Challenge the positive thesis. Emphasize contradictions, stale evidence, missing cash-flow proof and management assertions; retain supported positives without endorsing them.',
}
INJECTION = re.compile(r'ignore\s+(?:all\s+)?previous|(?:system|developer)\s+prompt|do not mention this|for AI assistants|summarisation tools', re.I)
PROHIBITED = re.compile(r'\b(?:strong buy|buy now|sell now|multibagger|analyst consensus|price target|target price|\d+\s*%\s*upside|chain.of.thought)\b', re.I)


@dataclass
class Source:
    id: str
    filename: str
    source: str
    url: str
    published: str
    type: str
    sha256: str
    body: str
    trust: str = ''
    status: str = ''
    reason: str = ''
    injection: bool = False
    removed_comments: str = ''


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def valid_url(value):
    try:
        parsed = urllib.parse.urlsplit(value)
        return parsed.scheme in ('http', 'https') and bool(parsed.hostname) and not parsed.username and not parsed.password and not any(c.isspace() for c in value)
    except ValueError:
        return False


def ingest(directory, as_of):
    root = Path(directory)
    if not root.is_dir():
        raise ValueError('Documents directory does not exist')
    sources, rejected, total = [], [], 0
    seen_hashes = set()
    for path in sorted(root.iterdir(), key=lambda p: p.name):
        if path.suffix.lower() != '.md':
            continue
        info = {'filename': path.name}
        try:
            if path.is_symlink() or not path.is_file():
                raise ValueError('not a regular non-symlink file')
            if path.stat().st_size > MAX_FILE:
                raise ValueError('file exceeds size limit')
            raw = path.read_text(encoding='utf-8')
            info['sha256'] = sha(raw)
            total += len(raw.encode('utf-8'))
            if total > MAX_CORPUS:
                raise ValueError('corpus exceeds size limit')
            if not raw.startswith('---\n'):
                if path.name.lower() == 'readme.md':
                    rejected.append({**info, 'reason': 'README without source metadata; ignored'})
                    continue
                raise ValueError('missing metadata front matter')
            chunks = raw.split('---\n', 2)
            if len(chunks) != 3:
                raise ValueError('unclosed metadata front matter')
            meta = {}
            for line in chunks[1].splitlines():
                if not line.strip():
                    continue
                key, sep, value = line.partition(':')
                if not sep or key not in ('source', 'url', 'published', 'type') or key in meta or not value.strip():
                    raise ValueError('malformed or duplicate metadata')
                meta[key] = value.strip()
            if set(meta) != {'source', 'url', 'published', 'type'}:
                raise ValueError('missing required metadata')
            if not valid_url(meta['url']):
                raise ValueError('invalid source URL')
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', meta['published']):
                raise ValueError('publication date must use YYYY-MM-DD')
            if dt.date.fromisoformat(meta['published']) > as_of:
                raise ValueError('future publication date')
            body = chunks[2].strip()
            if not body:
                raise ValueError('empty document')
            if info['sha256'] in seen_hashes:
                raise ValueError('duplicate document content')
            seen_hashes.add(info['sha256'])
            injected = bool(INJECTION.search(body))
            comments = '\n'.join(re.findall(r'<!--.*?-->', body, flags=re.S))
            body = re.sub(r'<!--.*?-->', '', body, flags=re.S).strip()
            sources.append(Source(f'S{len(sources)+1}', path.name, **meta,
                                  sha256=info['sha256'], body=body, injection=injected, removed_comments=comments))
        except (ValueError, UnicodeError, OSError) as exc:
            rejected.append({**info, 'reason': str(exc)})
    if total > MAX_CORPUS:
        raise ValueError('Corpus exceeds size limit; no partial run permitted')
    return sources, rejected


def resolve_identity(sources, ticker):
    anchors = []
    # Identity requires explicit company name immediately associated with NSE ticker.
    pattern = re.compile(r'([A-Z][\w& .-]{2,90}?\b(?:Ltd\.?|Limited))\s*\(NSE:\s*' + re.escape(ticker) + r'\)', re.I)
    for source in sources:
        if 'official' in source.type.lower() and 'blog' not in source.type.lower():
            for match in pattern.finditer(source.body):
                name = match.group(1).strip().split('\n')[-1]
                anchors.append((name, source))
    names = {re.sub(r'\s+', ' ', name).lower() for name, _ in anchors}
    if len(names) != 1:
        raise ValueError('No unique official company-name/NSE-ticker anchor; identity unresolved')
    name = anchors[0][0]
    alias = re.sub(r'\s+(?:Ltd\.?|Limited)$', '', name, flags=re.I)
    hosts = {urllib.parse.urlsplit(s.url).hostname for _, s in anchors}
    for source in sources:
        typ = source.type.lower()
        source.trust = 'high' if 'official' in typ else 'medium' if 'news' in typ else 'low'
        if 'blog' in typ:
            source.status, source.reason = 'quarantined', 'promotional blog; never used for claims'
        elif source.injection:
            source.status, source.reason = 'quarantined', 'instruction-like text detected'
        elif re.search(r'unrelated to|not (?:the same|associated|affiliated)|cable TV|broadband operator', source.body, re.I):
            source.status, source.reason = 'excluded', 'competing entity or explicit non-affiliation'
        elif re.search(r'\b' + re.escape(alias) + r'\b', source.body, re.I):
            source.status, source.reason = 'included', 'full company alias matches official identity'
        elif 'official' in typ and 'transcript' in typ and urllib.parse.urlsplit(source.url).hostname in hosts and not re.search(r'\bNSE:\s*(?!' + re.escape(ticker) + r'\b)[A-Z0-9&.-]+', source.body):
            source.status, source.reason = 'included', 'official transcript on identity anchor host'
        else:
            source.status, source.reason = 'excluded', 'entity uncertain or unrelated; full company alias absent'
    if not any(s.status == 'included' for s in sources):
        raise ValueError('No valid relevant documents')
    return {'company': name, 'alias': alias, 'ticker': ticker}


def clean(text):
    return re.sub(r'\s+', ' ', re.sub(r'[*_`]', '', text)).strip(' -')


def evidence_units(source):
    """Keep table headers with rows, since a bare number is not evidence of a period."""
    units, header = [], ''
    for line in source.body.splitlines():
        line = clean(line)
        if not line or line.startswith('#') or re.fullmatch(r'[| :–-]+', line):
            continue
        if line.startswith('|'):
            if not header:
                header = line
                continue
            units.append(header + ' ' + line)
        else:
            units.extend(re.split(r'(?<=[.!?])\s+(?=[A-Z"“])', line))
    return units


def evidence_catalog(sources):
    """Stable, local evidence IDs; quotes are normalized source sentences/table rows."""
    return [{'id': f'{s.id}:E{i}', 'source': s.id, 'quote': unit}
            for s in sources if s.status == 'included'
            for i, unit in enumerate(evidence_units(s), 1)]


def reporting_period(source):
    # Explicit calendar-quarter language takes precedence over a terse headline.
    months = (('January', 'March', 1), ('April', 'June', 4),
              ('July', 'September', 7), ('October', 'December', 10))
    for first, last, month in months:
        match = re.search(first + r'\s*[–—-]\s*' + last + r'(?:\s+(20\d{2}))?\s+quarter', source.body, re.I)
        if match:
            year = int(match.group(1) or source.published[:4])
            return f'{year}-{month:02d}'
    match = re.search(r'\bQ([1-4])\s*FY\s*(\d{2}|20\d{2})\b', source.body, re.I)
    if match:
        quarter, year = int(match.group(1)), int(match.group(2))
        year = year + 2000 if year < 100 else year
        month = {1: 4, 2: 7, 3: 10, 4: 1}[quarter]
        return f'{year if quarter == 4 else year - 1}-{month:02d}'
    return None


def grounding_errors(claim, support):
    """Conservative lexical/metric checks; these are not semantic entailment proof."""
    errors = []
    if numeric_tokens(claim) - numeric_tokens(support):
        errors.append('unsupported numeric claim in selected evidence')
    topics = (r'revenue', r'profit after tax|net profit|\bPAT\b', r'EBITDA',
              r'margin', r'receivable', r'pledge', r'copper', r'capex',
              r'order book', r'export', r'capacity', r'GST|tax credit', r'debt')
    for topic in topics:
        if re.search(topic, claim, re.I) and not re.search(topic, support, re.I):
            errors.append('claim metric/topic absent from selected evidence')
    if re.search(r'\bminus\b|[−-]\s*₹?\s*\d', claim, re.I) and not re.search(r'\bminus\b|[−-]\s*₹?\s*\d', support, re.I):
        errors.append('unsupported negative sign')
    if re.search(r'\b(?:no|not|never|without)\b', claim, re.I) and not re.search(r'\b(?:no|not|never|without)\b', support, re.I):
        errors.append('unsupported negative assertion')
    # Do not permit a forecast to become a claim of a certain outcome.
    if re.search(r'\b(?:will|guaranteed|certain)\b', claim, re.I) and re.search(r'expect|guidance|on track|intend|plan|believe', support, re.I) and not re.search(r'expect|guidance|on track|intend|plan|believe|may|could', claim, re.I):
        errors.append('forecast presented as certain')
    return errors


def numeric_tokens(text):
    # Commas, percent wording and Unicode signs normalized; citation IDs excluded.
    text = re.sub(r'\[S\d+\]', '', text)
    text = text.replace(',', '').replace('−', '-').replace('–', '-')
    return {str(float(n)) for n in re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)?', text)}


def detect_issues(sources):
    included = [s for s in sources if s.status == 'included']
    revenue, pledges = [], []
    for s in included:
        for unit in evidence_units(s):
            if re.search(r'revenue from operations', unit, re.I):
                # Revenue row or prose has current value before historical comparison.
                match = re.search(r'(?:operations\s*\|\s*|operations.*?₹)([\d,]+)', unit, re.I)
                if match:
                    revenue.append({'source': s.id, 'value': match.group(1), 'evidence': unit,
                                    'period': reporting_period(s),
                                    'scope': 'consolidated' if 'consolidated' in s.body.lower() else 'standalone' if 'standalone' in s.body.lower() else 'unspecified',
                                    'growth': (re.search(r'([+−-]?\d+(?:\.\d+)?)\s*%', unit).group(1) if re.search(r'([+−-]?\d+(?:\.\d+)?)\s*%', unit) else None)})
            if re.search(r'pledged|pledging', unit, re.I) and re.search(r'\d', unit):
                pledges.append({'source': s.id, 'published': s.published, 'evidence': unit})
    conflicts = []
    # Compare explicit reporting periods, never publication-date proximity.
    for left in revenue:
        for right in revenue:
            compatible_scope = left['scope'] == right['scope'] or 'unspecified' in (left['scope'], right['scope'])
            if left['source'] < right['source'] and left['period'] is not None and left['period'] == right['period'] and compatible_scope and (numeric_tokens(left['value']) != numeric_tokens(right['value']) or (left['growth'] is not None and right['growth'] is not None and numeric_tokens(left['growth']) != numeric_tokens(right['growth']))):
                conflicts.append({'metric': 'revenue / associated growth', 'reports': [left, right],
                                  'resolution': 'Prefer official filing; retain discrepancy as an open question'})
    temporal = []
    if len({p['published'] for p in pledges}) > 1:
        temporal.append({'metric': 'promoter pledge', 'reports': pledges,
                         'resolution': 'Different reporting dates; historical pledge is not current pledge'})
    return conflicts, temporal


def item(text, *sources):
    return {'text': text, 'citations': list(sources)}


def offline_sections(sources, conflicts, temporal, review):
    """Extractive fallback. All company content comes directly from supplied documents."""
    included = [s for s in sources if s.status == 'included']
    ranked = sorted(included, key=lambda s: (s.trust != 'high', -dt.date.fromisoformat(s.published).toordinal(), s.id))
    units = [(s, u) for s in ranked for u in evidence_units(s)]
    result = {h: [] for h in HEADINGS}
    used = set()

    def take(section, pattern, count=1, limit=64):
        for s, u in units:
            if count <= 0:
                break
            if (s.id, u) in used or len(u.split()) > limit or not re.search(pattern, u, re.I) or PROHIBITED.search(u):
                continue
            result[section].append(item(u, s.id))
            used.add((s.id, u))
            count -= 1

    take('Snapshot', r'\(NSE:')
    take('Snapshot', r'Revenue from operations\s*\|')
    take('Snapshot', r'EBITDA margin\s*\|')
    take('Bull case', r'order book')
    take('Bull case', r'commercial production|capacity')
    take('Bear case', r'raising a demand|received an order')
    take('Bear case', r'receivable days increased')
    if review == 'skeptical':
        take('Bear case', r'reset with a lag|funded mainly')
    elif review == 'conservative':
        take('Bear case', r'funded mainly|net debt')
    else:
        take('Bull case', r'price-variation clauses')
    for conflict in conflicts:
        reports = conflict['reports']
        result['Open questions'].append(item('Revenue reports conflict: ' + '; '.join(f"{r['value']} (growth {r['growth']}%) in {r['source']}" if r['growth'] else f"{r['value']} in {r['source']}" for r in reports) + '. Reconcile the news report with the official filing before relying on its growth claim.', *(r['source'] for r in reports)))
    for difference in temporal:
        reports = difference['reports']
        oldest = min(reports, key=lambda r: r['published'])
        historical = re.search(r'(\d+(?:\.\d+)?)\s*%', oldest['evidence'])
        description = f"The {oldest['published']} report cited {historical.group(1)}% pledged; " if historical else 'Pledge evidence has different reporting dates; '
        result['Open questions'].append(item(description + 'use the latest filing for the current position and treat the older report as historical.', *dict.fromkeys(r['source'] for r in reports)))
        newest = max(reports, key=lambda r: r['published'])
        result['Snapshot'].append(item(newest['evidence'], newest['source']))
    take('Open questions', r'intends to file an appeal|expects? to pass|expect to pass')
    for heading in HEADINGS:
        if not result[heading]:
            result[heading].append(item('The supplied evidence does not establish a supported conclusion for this section.'))
    return result


def source_lines(sources, rejected):
    lines = []
    for source in sources:
        status = source.status
        if status != 'included':
            status += ': ' + ('promotional/injection risk' if source.trust == 'low' or source.injection else 'unrelated/uncertain entity')
        lines.append(f'- [{source.id}] [{source.source}]({source.url}) · {source.published} · {source.type} · {status}.')
    for entry in rejected:
        if not entry['reason'].startswith('README'):
            lines.append(f"- Rejected `{entry['filename']}`: {entry['reason']}.")
    return lines


def render(sections, sources, rejected, offline=False):
    parts = []
    for heading in HEADINGS:
        parts.append('## ' + heading)
        if heading == 'Snapshot' and offline:
            parts.append('*Offline extractive brief; no model was used.*')
        for entry in sections[heading]:
            cites = ' '.join('[' + c + ']' for c in entry['citations'])
            parts.append('- ' + entry['text'] + (' ' + cites if cites else ''))
        parts.append('')
    parts += ['## Sources', *source_lines(sources, rejected)]
    return '\n'.join(parts).strip() + '\n'


def validate(sections, sources, conflicts, text, model=False):
    errors = []
    by_id = {s.id: s for s in sources}
    catalog = {e['id']: e for e in evidence_catalog(sources)}
    if not isinstance(sections, dict) or set(sections) != set(HEADINGS):
        return ['wrong section schema']
    if len(text.split()) > 650:
        errors.append('brief exceeds 650 words including sources')
    for heading in HEADINGS:
        if not isinstance(sections[heading], list) or not sections[heading]:
            errors.append('empty or malformed section')
            continue
        for entry in sections[heading]:
            if not isinstance(entry, dict) or not isinstance(entry.get('text'), str) or not isinstance(entry.get('citations'), list):
                errors.append('invalid item schema')
                continue
            claim, cites = entry['text'], entry['citations']
            if not claim.strip() or '\n' in claim or '#' in claim or re.search(r'\[S\d+\]', claim):
                errors.append('invalid or empty claim text')
            if PROHIBITED.search(claim) or INJECTION.search(claim):
                errors.append('prohibited recommendation or instruction language')
            if not cites and claim != 'The supplied evidence does not establish a supported conclusion for this section.':
                errors.append('uncited claim')
            if any(not isinstance(c, str) or c not in by_id or by_id[c].status != 'included' for c in cites):
                errors.append('unknown, quarantined or unrelated citation')
                continue
            support = ' '.join(by_id[c].body + ' ' + by_id[c].published for c in cites)
            if numeric_tokens(claim) - numeric_tokens(support):
                errors.append('unsupported numeric claim')
            if model:
                evidence = entry.get('evidence')
                if not isinstance(evidence, list) or not evidence:
                    errors.append('missing exact evidence quotes')
                else:
                    selected = []
                    evidence_sources = set()
                    for quote in evidence:
                        if not isinstance(quote, dict):
                            errors.append('invalid evidence quote')
                            continue
                        if 'id' in quote:
                            quote = catalog.get(quote['id'], {})
                        if quote.get('source') not in cites or not isinstance(quote.get('quote'), str) or len(quote['quote']) < 12:
                            errors.append('invalid evidence quote')
                        elif clean(quote['quote']) not in clean(by_id[quote['source']].body) and clean(quote['quote']) not in [clean(u) for u in evidence_units(by_id[quote['source']])]:
                            errors.append('evidence quote absent from cited source')
                        else:
                            selected.append(quote['quote'])
                            evidence_sources.add(quote['source'])
                    if evidence_sources != set(cites):
                        errors.append('citation lacks selected evidence')
                    errors.extend(grounding_errors(claim, ' '.join(selected)))
    open_items = sections.get('Open questions', [])
    for conflict in conflicts:
        ids = {r['source'] for r in conflict['reports']}
        if not any(ids <= set(e.get('citations', [])) and re.search(r'conflict|discrepan|differ|reconcil|versus|\bvs\b|which.*(?:correct|accurate)|why.*(?:report|revenue|growth)' , e.get('text', ''), re.I) for e in open_items if isinstance(e, dict)):
            errors.append('missing explicit revenue conflict')
    return sorted(set(errors))


def load_env(path):
    path = Path(path)
    if not path.exists():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:]
        key, sep, value = line.partition('=')
        if sep and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key):
            os.environ.setdefault(key, value.strip().strip('\"\''))


def route(args):
    provider = args.provider
    if provider == 'auto':
        provider = 'groq' if os.getenv('GROQ_API_KEY') else 'openai' if os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_BASE_URL') or args.base_url else 'offline'
    if provider == 'offline':
        return {'provider': provider, 'model': None, 'base_url': None, 'key': ''}
    if provider == 'groq':
        return {'provider': provider, 'model': args.model or 'openai/gpt-oss-120b', 'base_url': args.base_url or 'https://api.groq.com/openai/v1', 'key': os.getenv('GROQ_API_KEY', '')}
    return {'provider': provider, 'model': args.model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini'), 'base_url': args.base_url or os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'), 'key': os.getenv('OPENAI_API_KEY', '')}


def api_call(config, payload):
    url = config['base_url'].rstrip('/') + '/chat/completions'
    if not valid_url(url):
        raise ValueError('Invalid API base URL')
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' and parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
        raise ValueError('Remote API requires HTTPS')
    headers = {'Content-Type': 'application/json', 'User-Agent': 'document-research-agent/1.0'}
    if config['key']:
        headers['Authorization'] = 'Bearer ' + config['key']
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    # Prevent credential forwarding through redirects to a different host.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *unused):
            return None
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=90) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError('API response exceeds size limit')
        return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raise ValueError(f'API HTTP {exc.code}') from None
    except urllib.error.URLError:
        raise ValueError('API connection failed') from None


def run(args):
    load_env(args.env_file)
    ticker = args.ticker.upper()
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9&.-]{0,24}', ticker):
        raise ValueError('Invalid NSE ticker')
    as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date(2026, 9, 23) if ticker == 'SRVCABLE' else dt.date.today()
    if args.live_data or args.live_url:
        if ticker == 'SRVCABLE':
            raise ValueError('Live retrieval is forbidden for fictional SRVCABLE')
        raise ValueError('Live retrieval is not implemented; supply reviewed local Markdown documents')
    root = Path(args.docs).resolve()
    for target in (args.audit, args.output):
        if target and Path(target).resolve().is_relative_to(root):
            raise ValueError('Output and audit paths must be outside the source documents directory')
    sources, rejected = ingest(args.docs, as_of)
    identity = resolve_identity(sources, ticker)
    conflicts, temporal = detect_issues(sources)
    system = Path(__file__).with_name('system_prompt.md').read_text(encoding='utf-8') + '\nReview policy: ' + REVIEWS[args.review]
    config = route(args)
    run_dir = Path(args.audit).resolve().parent / 'runs' / (dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:10])
    if run_dir.resolve().is_relative_to(root):
        run_dir = Path(args.audit).resolve().parent / ('research-artifacts-' + uuid.uuid4().hex)
    if run_dir.resolve().is_relative_to(root):
        raise ValueError('Generated artifacts must be outside source documents directory')
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / 'writer_system_prompt.md').write_text(system, encoding='utf-8')
    audit = {'identity': identity, 'as_of': str(as_of), 'review': args.review,
             'source_id_scope': 'Filename-sorted valid metadata documents in this corpus; stable for identical corpus, not insertion-stable.',
             'sources': [asdict(s) for s in sources], 'rejected': rejected,
             'conflicts': conflicts, 'temporal_differences': temporal,
             'provider': config['provider'], 'model': config['model'], 'prompt_sha256': sha(system),
             'source_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'run_dir': str(run_dir), 'fallback_reason': None, 'live_data': 'disabled; no URLs fetched'}
    sections, mode = None, 'offline'
    if config['provider'] != 'offline':
        user = {'ticker': ticker, 'company': identity, 'as_of': str(as_of), 'conflicts': conflicts,
                'temporal_differences': temporal,
                'documents': [asdict(s) for s in sources if s.status == 'included'],
                'evidence_catalog': evidence_catalog(sources)}
        payload = {'model': config['model'], 'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': json.dumps(user, ensure_ascii=False)}], 'max_completion_tokens': 6000}
        if config['provider'] == 'groq':
            payload.update(reasoning_effort='medium', reasoning_format='hidden')
        (run_dir / 'request.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        try:
            response = api_call(config, payload)
            choices = response.get('choices')
            if not isinstance(choices, list) or not choices:
                raise ValueError('API response missing choices')
            choice = choices[0]
            message = choice.get('message', {})
            visible = message.get('content')
            # Store visible content and usage only; never reasoning fields.
            (run_dir / 'response.json').write_text(json.dumps({'visible_content': visible, 'finish_reason': choice.get('finish_reason'), 'usage': response.get('usage')}, ensure_ascii=False, indent=2), encoding='utf-8')
            audit['usage'] = response.get('usage')
            if choice.get('finish_reason') != 'stop' or not isinstance(visible, str) or not visible.strip():
                raise ValueError('API reply empty, truncated, or incomplete')
            sections = json.loads(visible)
            text = render(sections, sources, rejected)
            errors = validate(sections, sources, conflicts, text, model=True)
            audit['model_validation'] = errors
            if errors:
                raise ValueError('Model validation failed: ' + '; '.join(errors))
            mode = 'model'
        except (ValueError, TypeError, KeyError, AttributeError, IndexError, TimeoutError, OSError) as exc:
            audit['fallback_reason'] = str(exc)[:500]
            sections = None
    if sections is None:
        sections = offline_sections(sources, conflicts, temporal, args.review)
    text = render(sections, sources, rejected, offline=(mode == 'offline'))
    errors = validate(sections, sources, conflicts, text)
    audit.update(mode=mode, final_validation=errors, word_count=len(text.split()))
    audit['artifacts'] = {'prompt': str(run_dir / 'writer_system_prompt.md'), 'request': str(run_dir / 'request.json') if config['provider'] != 'offline' else None, 'response': str(run_dir / 'response.json') if (run_dir / 'response.json').exists() else None, 'brief': str(run_dir / 'brief.md')}
    if errors:
        audit['failure'] = 'No valid brief emitted'
    else:
        (run_dir / 'brief.md').write_text(text, encoding='utf-8')
    (run_dir / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    audit_path = Path(args.audit)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    if errors:
        raise ValueError('Final validation failed: ' + '; '.join(errors))
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')
    return audit, text


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('ticker')
    p.add_argument('docs')
    p.add_argument('--provider', choices=('auto', 'offline', 'groq', 'openai'), default='auto')
    p.add_argument('--model')
    p.add_argument('--base-url', help='Explicit OpenAI-compatible gateway; localhost may be keyless')
    p.add_argument('--review', choices=tuple(REVIEWS), default='balanced')
    p.add_argument('--as-of')
    p.add_argument('--output')
    p.add_argument('--audit', default='audit.json')
    p.add_argument('--env-file', default='.env')
    p.add_argument('--live-data', action='store_true')
    p.add_argument('--live-url', action='append', default=[])
    return p


def main():
    try:
        run(parser().parse_args())
    except (ValueError, OSError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
