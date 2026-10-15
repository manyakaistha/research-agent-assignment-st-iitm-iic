"""Narrow, standard-library adapters for explicitly allowlisted official releases."""
import datetime as dt
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit

MAX_RAW_HTML = 2_000_000


def official_html_url(url):
    parsed = urlsplit(url)
    return (parsed.scheme == 'https' and parsed.hostname == 'www.wipro.com'
            and parsed.port in (None, 443)
            and parsed.path.startswith('/newsroom/press-releases/'))


class ReleaseParser(HTMLParser):
    """Collect semantic blocks only inside release text/article containers."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.blocks = []
        self.parts = []
        self.block = None
        self.tables = 0
        self.images = 0

    def flush(self):
        text = re.sub(r'\s+', ' ', ''.join(self.parts)).strip()
        if text:
            self.blocks.append(text)
        self.parts, self.block = [], None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else ('', False, False)
        scope = parent[1] or tag in ('article', 'main') or 'cmp-text' in attrs.get('class', '').split()
        excluded = parent[2] or tag in ('script', 'style', 'nav', 'header', 'footer', 'noscript', 'template', 'table') or 'hidden' in attrs or attrs.get('aria-hidden') == 'true'
        if tag == 'img' and (scope or 'infographics-image' in attrs.get('class', '').split()) and not parent[2]:
            self.images += 1
        if tag == 'table' and scope and not parent[2]:
            self.flush()
            self.tables += 1
        if scope and not excluded:
            if tag in ('p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                self.flush()
                self.block = tag
            elif tag == 'br':
                self.parts.append(' ')
            elif tag == 'sup' and self.block:
                self.parts.append(' [')
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append((tag, scope, excluded))

    def handle_endtag(self, tag):
        if self.stack and not self.stack[-1][2]:
            if tag == 'sup' and self.block:
                self.parts.append('] ')
            if tag == self.block:
                self.flush()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.block and self.stack and self.stack[-1][1] and not self.stack[-1][2]:
            self.parts.append(data)


def normalize_wipro_html(text, url):
    if not official_html_url(url):
        raise ValueError('HTML source is not an allowlisted official Wipro press release')
    parser = ReleaseParser()
    try:
        parser.feed(text)
        parser.close()
        parser.flush()
    except Exception as exc:
        raise ValueError('HTML parsing failed: ' + type(exc).__name__) from None
    if not parser.blocks:
        raise ValueError('HTML release has no extractable paragraph, heading or list content')
    datelines = []
    for block in parser.blocks:
        match = re.search(r'[–—-]\s*([A-Z][a-z]+ \d{1,2}, \d{4})\s*:', block)
        if match and re.search(r'Wipro Limited\s*\(', block, re.I):
            try:
                date = dt.datetime.strptime(match.group(1), '%B %d, %Y').date()
            except ValueError:
                raise ValueError('HTML release dateline has an invalid date') from None
            datelines.append((date, block))
    if not datelines or len({date for date, _ in datelines}) != 1:
        raise ValueError('HTML release requires a unique publication dateline; date not inferred from URL')
    published, date_evidence = datelines[0]
    body = '\n\n'.join(parser.blocks)
    identity = re.search(r'Wipro Limited\s*\([^)]*\bNSE:\s*WIPRO(?=\s*[,;)])[^)]*\)', body, re.I)
    if not identity:
        raise ValueError('HTML release lacks native Wipro Limited/NSE: WIPRO identity')
    markdown = ('---\nsource: Wipro official press release\nurl: ' + url + '\npublished: '
                + str(published) + '\ntype: official company press release\n---\n' + body + '\n')
    return markdown, {'published': str(published), 'date_evidence': date_evidence,
                      'company_identity': identity.group(0),
                      'coverage_gaps': ([f'{parser.tables} HTML table(s) omitted; table metrics unavailable unless repeated in extracted prose.'] if parser.tables else []) + ([f'{parser.images} image(s) omitted; image-only content unavailable (no OCR).'] if parser.images else [])}

# These adapters deliberately support only the observed release templates/paths.
_NATIVE_RELEASES = {
    ('news.coforge.com', '/newsroom/press-release/coforge-delivers-49-yoy-growth-pat-increases-110-yoy'): ('COFORGE', 'Coforge Limited', 'coforge'),
    ('www.techmahindra.com', '/insights/press-releases/techmahindra-q2-fy27-results/'): ('TECHM', 'Tech Mahindra', 'techmahindra'),
    ('www.persistent.com', '/media/press-releases/q1-fy27-results/'): ('PERSISTENT', 'Persistent Systems', 'persistent'),
}


def native_release(url):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.port not in (None, 443)
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        return None
    return _NATIVE_RELEASES.get((parsed.hostname, parsed.path))


def native_identity(body, url, ticker):
    """Return an observed on-host brand anchor, without inventing a legal suffix."""
    adapter = native_release(url)
    if not adapter or adapter[0] != ticker:
        return None
    brand = adapter[1]
    pattern = re.compile(r'(?<![\w&.-])' + re.escape(brand) + r'\s*\([^()\n]*\bNSE:\s*'
                         + re.escape(ticker) + r'(?=\s*[,;)])[^()\n]*\)', re.I)
    match = pattern.search(body)
    return (brand, match.group(0)) if match else None


class _Node:
    def __init__(self, tag='', attrs=None):
        self.tag, self.attrs, self.children = tag, attrs or {}, []

    def text(self):
        return re.sub(r'\s+', ' ', ''.join(
            c if isinstance(c, str) else (' ' + c.text() + ' ' if c.tag in
            ('ul', 'ol', 'li', 'p', 'div', 'br') else c.text())
            for c in self.children)).strip()

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, _Node):
                yield from child.walk()


class _ReleaseTree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, dict(attrs))
        node.parent = self.stack[-1]
        self.stack[-1].children.append(node)
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _visible(node):
    return (node.tag not in ('script', 'style', 'nav', 'header', 'footer', 'noscript', 'template')
            and 'hidden' not in node.attrs and node.attrs.get('aria-hidden') != 'true'
            and not re.search(r'display\s*:\s*none|visibility\s*:\s*hidden', node.attrs.get('style', ''), re.I))


def _prune(node):
    node.children = [c for c in node.children if isinstance(c, str) or _visible(c)]
    for c in node.children:
        if isinstance(c, _Node):
            _prune(c)


def normalize_html(text, url):
    adapter = native_release(url)
    if adapter is None:
        return normalize_wipro_html(text, url)
    tree = _ReleaseTree()
    tree.feed(text)
    tree.close()
    _prune(tree.root)
    nodes = list(tree.root.walk())
    if adapter[2] == 'techmahindra':
        scopes = [n for n in nodes if n.tag == 'article' and 'node--type-press-release' in n.attrs.get('class', '').split()]
    elif adapter[2] == 'coforge':
        scopes = [n for n in nodes if n.tag == 'span' and n.attrs.get('id') == 'hs_cos_wrapper_post_body'
                  and n.parent.tag == 'div' and 'post-body' in n.parent.attrs.get('class', '').split()]
    else:
        scopes = [n for n in nodes if n.tag == 'main' and 'theme-main' in n.attrs.get('class', '').split()]
    if len(scopes) != 1:
        raise ValueError('HTML release requires a unique article container')
    scope = scopes[0]
    nodes = list(scope.walk())
    if adapter[2] == 'techmahindra':
        date_nodes = [n for n in nodes if n.tag == 'time' and n.attrs.get('class') == 'datetime']
    elif adapter[2] == 'coforge':
        date_nodes = [n for n in nodes if n.tag == 'p' and re.search(r'[A-Z][a-z]+ \d{1,2}, \d{4}\s*[–—-]\s*Coforge Limited\s*\(NSE:\s*COFORGE\)', n.text())]
    else:
        date_nodes = [n for n in nodes if n.tag == 'p' and 'date' in n.attrs.get('class', '').split()]
    dates = []
    for n in date_nodes:
        try:
            date_text = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})\s*[–—-]\s*Coforge Limited', n.text()).group(1) if adapter[2] == 'coforge' else n.text()
            dates.append((dt.datetime.strptime(date_text, '%B %d, %Y').date(), n.text()))
        except ValueError:
            raise ValueError('HTML release article date is invalid') from None
    if not dates or len({d for d, _ in dates}) != 1:
        raise ValueError('HTML release requires a unique article publication date; date not inferred from URL')
    published, date_evidence = dates[0]
    titles = [n.text() for n in (tree.root.walk() if adapter[2] == 'coforge' else nodes) if n.tag == 'h1']
    if len(titles) != 1:
        raise ValueError('HTML release requires a unique title')
    title = titles[0]
    if adapter[2] == 'coforge':
        periods = re.findall(r'quarter ended [A-Z][a-z]+ \d{1,2}, \d{4}', date_evidence)
        if len(periods) != 1:
            raise ValueError('HTML release requires an explicit quarter-end in its dateline')
        title += ' | ' + periods[0]
    blocks, gaps = [], []
    heading = ''

    def extract(node):
        nonlocal heading
        if node.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            heading = node.text()
            blocks.append(heading)
        elif node.tag == 'table':
            rows = [n for n in node.walk() if n.tag == 'tr']
            cells = [[c for c in r.children if isinstance(c, _Node) and c.tag in ('td', 'th')] for r in rows]
            merged = any(c.attrs.get('rowspan', '1') != '1' or c.attrs.get('colspan', '1') != '1' for row in cells for c in row)
            if (merged or len(cells) < 2 or len(cells[0]) < 2
                    or any(len(row) != len(cells[0]) for row in cells)
                    or any(not c.text() for c in cells[0][1:])
                    or any(not row[0].text() for row in cells[1:])):
                gaps.append('HTML table omitted: merged or ambiguous header/row structure; table metrics unavailable.')
                return
            header = [c.text() for c in cells[0]]
            if len(set(header[1:])) != len(header[1:]):
                gaps.append('HTML table omitted: duplicate column headings; table metrics unavailable.')
                return
            for row in cells[1:]:
                fields = [header[i] + ': ' + row[i].text() for i in range(1, len(row)) if row[i].text()]
                caption = ' '.join(n.text() for n in node.parent.children if isinstance(n, _Node) and n.tag == 'figcaption')
                blocks.append(title + ' | ' + heading + ' | ' + header[0] + ' | ' + row[0].text() + ' | ' + '; '.join(fields) + (' | ' + caption if caption else ''))
        elif node.tag == 'li':
            # A whole outer list item keeps its amount and nested growth qualifiers together.
            if node.text():
                blocks.append(title + ' | ' + heading + ' | ' + node.text())
        elif node.tag in ('p', 'figcaption', 'blockquote'):
            if node.text():
                blocks.append(node.text())
        else:
            for child in node.children:
                if isinstance(child, _Node):
                    extract(child)
    if adapter[2] == 'persistent':
        articles = [n for n in nodes if n.tag == 'section' and 'post-single' in n.attrs.get('class', '').split()]
        if len(articles) != 1:
            raise ValueError('HTML release requires a unique post container')
        blocks.append(title)
        extract(articles[0])
    else:
        extract(scope)
    body = '\n\n'.join(blocks)
    identity = native_identity(body, url, adapter[0])
    if not identity:
        raise ValueError('HTML release lacks native company/NSE ticker identity')
    images = sum(n.tag == 'img' for n in nodes)
    if images:
        gaps.append(f'{images} image(s) omitted; image-only content unavailable (no OCR).')
    markdown = ('---\nsource: ' + adapter[1] + ' official press release\nurl: ' + url
                + '\npublished: ' + str(published) + '\ntype: official company press release\n---\n' + body + '\n')
    return markdown, {'published': str(published), 'date_evidence': date_evidence,
                      'company_identity': identity[1], 'coverage_gaps': gaps}
