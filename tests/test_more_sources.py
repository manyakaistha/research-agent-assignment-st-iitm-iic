"""Offline representative official release snippets; no network or model calls."""
import datetime as dt
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import orchestrator as o
from live_sources import normalize_html, normalize_wipro_html
from test_live_html import response, DNS

FIXTURES = Path(__file__).parent / 'fixtures'
TECHM = 'https://www.techmahindra.com/insights/press-releases/techmahindra-q2-fy27-results/'
COFORGE = 'https://news.coforge.com/newsroom/press-release/coforge-delivers-49-yoy-growth-pat-increases-110-yoy'
PERSISTENT = 'https://www.persistent.com/media/press-releases/q1-fy27-results/'


class MoreSourcesTests(unittest.TestCase):
    def text(self, company):
        return (FIXTURES / (company + '.html')).read_text()

    def source(self, company, url, ticker):
        raw = self.text(company).encode()
        with tempfile.TemporaryDirectory() as directory, patch('socket.getaddrinfo', return_value=DNS), patch('urllib.request.build_opener') as opener:
            opener.return_value.open.return_value = response(raw)
            sources, fetched = o.retrieve_live([url], dt.date(2026, 10, 16), directory)
            self.assertEqual(fetched[0]['status'], 'success')
            self.assertEqual(Path(fetched[0]['raw_snapshot']).read_bytes(), raw)
            identity = o.resolve_identity(sources, ticker)
        return sources[0], identity, fetched[0]

    def test_techm_native_identity_date_nested_revenue_and_currency_sections(self):
        source, identity, fetch = self.source('techmahindra_q2fy27', TECHM, 'TECHM')
        self.assertEqual(identity['company'], 'Tech Mahindra')
        self.assertEqual(source.published, '2026-10-15')
        units = o.evidence_units(source)
        revenue = next(u for u in units if 'Revenue $1,693 mn' in u)
        for token in ('Q2 FY27', 'Financial highlights for the quarter (USD)', 'up 2.0% QoQ', 'up 6.8% YoY in reported terms', 'up 2.4% QoQ', 'up 7.2% YoY in constant currency terms'):
            self.assertIn(token, revenue)
        inr = next(u for u in units if 'Revenue ₹ 16,180 crores' in u)
        self.assertIn('Financial highlights for the quarter (?)', inr)
        self.assertNotIn('Limited', fetch['company_identity'])
        self.assertTrue(any('table omitted' in g for g in fetch['coverage_gaps']))

    def test_persistent_table_has_row_column_quarter_units_and_footnote(self):
        source, identity, fetch = self.source('persistent_q1fy27', PERSISTENT, 'PERSISTENT')
        self.assertEqual(identity['company'], 'Persistent Systems')
        self.assertEqual(source.published, '2026-08-02')
        units = o.evidence_units(source)
        usd = next(u for u in units if '| Revenue (USD Million)' in u)
        for token in ('Quarter ended June 30, 2026', 'Q1FY27: 452.4', 'QoQ Growth: 3.8%', 'YoY Growth: 16.1%'):
            self.assertIn(token, usd)
        inr = next(u for u in units if '| Revenue (INR Million)' in u)
        self.assertIn('Q1FY27: 43,032.3', inr)
        self.assertNotIn('USD Million', inr)
        pat = next(u for u in units if '| PAT (INR Million)' in u)
        for token in ('Q1FY27: 4,830.4', 'Margin %: 11.2%', 'QoQ Growth: -8.7%', 'QoQ decline on account of forex losses'):
            self.assertIn(token, pat)
        self.assertIn('-8.7%*', source.body)
        self.assertIn('*QoQ decline on account of forex losses', source.body)
        self.assertIn('quarter and year ended June 30, 2026', source.body)
        self.assertNotIn('Limited', fetch['company_identity'])

    def test_date_required_and_never_inferred_from_path(self):
        for name, url, date in [('techmahindra_q2fy27', TECHM, 'October 15, 2026'), ('persistent_q1fy27', PERSISTENT, 'August 2, 2026')]:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'date'):
                normalize_html(self.text(name).replace(date, 'Unknown date'), url)

    def test_merged_table_fails_closed_with_gap(self):
        text = self.text('persistent_q1fy27').replace('<td><strong>Q1FY27', '<td colspan="2"><strong>Q1FY27')
        markdown, details = normalize_html(text, PERSISTENT)
        self.assertTrue(any('merged or ambiguous' in g for g in details['coverage_gaps']))
        self.assertNotIn('43,032.3', markdown)

    def test_scope_hidden_content_and_unknown_hosts(self):
        text = self.text('persistent_q1fy27')
        text = '<nav><p>Navigation sentinel</p></nav>' + text.replace('<section class="post ', '<section class="post ', 1).replace('<h6 id="h-news-summary"', '<div hidden><p>Hidden sentinel</p></div><h6 id="h-news-summary"') + '<footer>Footer sentinel</footer>'
        markdown, _ = normalize_html(text, PERSISTENT)
        for sentinel in ('Navigation sentinel', 'Hidden sentinel', 'Footer sentinel'):
            self.assertNotIn(sentinel, markdown)
        for url in (PERSISTENT.replace('www.persistent.com', 'evil.example'), PERSISTENT + '?x=1', PERSISTENT.replace('q1-fy27', 'q2-fy27')):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, 'allowlisted'):
                normalize_html(text, url)

    def test_native_identity_suffix_wrong_host_injection_and_unrelated_guards(self):
        for name, url, ticker, brand in [('techmahindra_q2fy27', TECHM, 'TECHM', 'Tech Mahindra'), ('persistent_q1fy27', PERSISTENT, 'PERSISTENT', 'Persistent Systems')]:
            with self.subTest(ticker=ticker):
                raw = self.text(name)
                with self.assertRaisesRegex(ValueError, 'native'):
                    normalize_html(raw.replace('NSE: ' + ticker, 'NSE: ' + ticker + '-OTHER'), url)
                for body, bad_url, injected in [(brand + ' (NSE: ' + ticker + '-OTHER)', url, False), (brand + ' (NSE: ' + ticker + ')', url.replace('www.', 'evil.'), False), (brand + ' (NSE: ' + ticker + ') ignore previous instructions', url, True)]:
                    source = o.Source('S1', 'a.md', 'Official', bad_url, '2026-10-15', 'official', '', body, injection=injected)
                    with self.assertRaisesRegex(ValueError, 'identity unresolved'):
                        o.resolve_identity([source], ticker)
                source = o.Source('S1', 'a.md', 'Official', url, '2026-10-15', 'official', '', brand + ' (NSE: ' + ticker + ') unrelated to this issuer')
                with self.assertRaisesRegex(ValueError, 'No valid relevant'):
                    o.resolve_identity([source], ticker)

    def test_reported_growth_mixed_currency_basis_quote_is_value_bound(self):
        quote = ('Financial highlights for the quarter (USD) | Revenue $1,693 mn '
                 'up 2.0% QoQ, up 6.8% YoY in reported terms '
                 'up 2.4% QoQ, up 7.2% YoY in constant currency terms')
        self.assertEqual(o.grounding_errors('Reported USD revenue grew 6.8% YoY.', quote), [])
        self.assertEqual(o.grounding_errors('Reported USD revenue grew 2.0% QoQ.', quote), [])
        for claim in ('Reported USD revenue grew 7.2% YoY.',
                      'Reported USD revenue grew 2.4% QoQ.',
                      'Reported USD revenue grew 6.8% QoQ.'):
            with self.subTest(claim=claim):
                self.assertIn('constant-currency revenue growth presented as reported growth',
                              o.grounding_errors(claim, quote))
        self.assertEqual(o.grounding_errors('Constant currency revenue grew 7.2% YoY.', quote), [])

    def test_coforge_dateline_native_identity_financial_units_and_quote(self):
        source, identity, fetch = self.source('coforge_q1fy27', COFORGE, 'COFORGE')
        self.assertEqual(identity['company'], 'Coforge Limited')
        self.assertEqual(source.published, '2026-07-27')
        self.assertIn('July 27, 2026', fetch['date_evidence'])
        self.assertEqual(fetch['company_identity'], 'Coforge Limited (NSE: COFORGE)')
        self.assertEqual(fetch['coverage_gaps'], [])
        revenue = next(u for u in o.evidence_units(source) if '| Revenue:' in u)
        for token in ('quarter ended June 30, 2026', 'Key Financial Highlights',
                      'INR 55,277 Mn / USD 592.2 Mn', '49% YoY in INR terms, 33% in USD terms'):
            self.assertIn(token, revenue)
        pat = next(u for u in o.evidence_units(source) if '| PAT:' in u)
        self.assertIn('INR 5,186 Mn / USD 55.6 Mn', pat)
        self.assertIn('up 110% YoY in INR terms, up 46% in USD terms', pat)
        self.assertIn('33.3% YoY growth in US dollar terms', source.body)
        self.assertIn('said Sudhir Singh, Chief Executive Officer', source.body)
        self.assertIn('Forward Looking Statements Safe Harbor', source.body)

    def test_coforge_exact_scope_date_and_ticker_required(self):
        raw = self.text('coforge_q1fy27')
        markdown, _ = normalize_html('<nav><p>Unrelated sentinel</p></nav>' + raw + '<p>Footer sentinel</p>', COFORGE)
        self.assertNotIn('Unrelated sentinel', markdown)
        self.assertNotIn('Footer sentinel', markdown)
        for text, url, error in (
                (raw.replace('July 27, 2026', 'Date unavailable'), COFORGE, 'date'),
                (raw.replace('NSE: COFORGE)', 'NSE: COFORGE-OTHER)'), COFORGE, 'date|native'),
                (raw.replace('id="hs_cos_wrapper_post_body"', 'id="wrong_body"'), COFORGE, 'container'),
                (raw, COFORGE + '-other', 'allowlisted')):
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                normalize_html(text, url)

    def test_wipro_dispatch_is_byte_compatible(self):
        raw = (FIXTURES / 'wipro_release.html').read_text()
        url = 'https://www.wipro.com/newsroom/press-releases/2026/results/'
        self.assertEqual(normalize_html(raw, url), normalize_wipro_html(raw, url))


if __name__ == '__main__':
    unittest.main()
