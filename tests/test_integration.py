import datetime as dt
from email.message import Message
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch

import orchestrator as o

PACK = Path(__file__).resolve().parents[1] / 'AI innovator assignment'


class LiveAndGatewayTests(unittest.TestCase):
    def test_gemini_route_payload_and_secret_redaction(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key-not-real'}, clear=True), patch('orchestrator.api_call', side_effect=ValueError('API HTTP 503')) as call:
            args = o.parser().parse_args(['SRVCABLE', str(PACK), '--provider', 'gemini', '--env-file', str(Path(temp)/'none'), '--output', str(Path(temp)/'brief.md'), '--audit', str(Path(temp)/'audit.json')])
            config = o.route(args)
            self.assertEqual(config['base_url'], 'https://generativelanguage.googleapis.com/v1beta/openai')
            self.assertEqual(config['model'], 'gemini-2.5-flash')
            audit, _ = o.run(args)
            payload = call.call_args.args[1]
            self.assertEqual(payload['response_format'], {'type': 'json_object'})
            self.assertNotIn('reasoning_format', payload)
            self.assertEqual(audit['mode'], 'offline')
            for path in Path(temp).rglob('*'):
                if path.is_file():
                    self.assertNotIn('test-key-not-real', path.read_text())
        with patch.dict(os.environ, {'GROQ_API_KEY': 'groq-test', 'OPENAI_BASE_URL': 'http://localhost:8080/v1'}, clear=True):
            args.provider = 'auto'
            self.assertEqual(o.route(args)['provider'], 'groq')

    def test_live_requires_optin_and_fictional_never_fetches(self):
        with patch('orchestrator.retrieve_live') as fetch:
            for opts in (['SRVCABLE', '--live-data'], ['SRVCABLE', '--live-url', 'https://example.org/source.md'], ['REALTICKER', '--live-url', 'https://example.org/source.md']):
                args = o.parser().parse_args([opts[0], str(PACK), *opts[1:]])
                with self.assertRaises(ValueError):
                    o.run(args)
            fetch.assert_not_called()

    def test_live_markdown_ingested_without_following_provenance_url(self):
        content = (PACK / 'ir_press_release_2026-08-08.md').read_bytes()
        response = io.BytesIO(content)
        response.headers = Message()
        response.headers['Content-Type'] = 'text/markdown'
        public_dns = [(2, 1, 6, '', ('93.184.216.34', 443))]
        with patch('socket.getaddrinfo', return_value=public_dns), patch('urllib.request.build_opener') as opener:
            opener.return_value.open.return_value = response
            sources, fetched = o.retrieve_live(['https://example.org/research.md'], dt.date(2026, 9, 23))
            self.assertEqual(len(sources), 1)
            self.assertEqual(sources[0].url, 'https://ir.sarvottamcables.example/press/q1fy27')
            self.assertEqual(fetched[0]['retrieved_url'], 'https://example.org/research.md')
            self.assertEqual(opener.return_value.open.call_count, 1)
            self.assertEqual(opener.return_value.open.call_args.args[0].full_url, 'https://example.org/research.md')

    def test_live_private_address_rejected_before_request(self):
        private_dns = [(2, 1, 6, '', ('127.0.0.1', 443))]
        with patch('socket.getaddrinfo', return_value=private_dns), patch('urllib.request.build_opener') as opener:
            with self.assertRaisesRegex(ValueError, 'private or local'):
                o.retrieve_live(['https://internal.example/research.md'], dt.date(2026, 9, 23))
            opener.assert_not_called()

    def test_additional_profit_conflict(self):
        sources, _ = o.ingest(PACK, dt.date(2026, 9, 23))
        o.resolve_identity(sources, 'SRVCABLE')
        news = next(s for s in sources if s.filename.startswith('businessdaily'))
        news.body = news.body.replace('₹82 crore', '₹99 crore')
        conflicts, _ = o.detect_issues(sources)
        self.assertTrue(any('profit after tax' in c['metric'] for c in conflicts))

    def test_intended_appeal_not_active_appeal(self):
        support = 'The company intends to file an appeal before the appropriate authority.'
        self.assertIn('intended appeal presented as filed', o.grounding_errors('The company is appealing the order.', support))
        self.assertEqual(o.grounding_errors('The company intends to file an appeal.', support), [])

    def test_fiscal_year_equivalence_and_questions(self):
        self.assertEqual(o.numeric_tokens('FY20-21 and FY21-22'), o.numeric_tokens('FY2020-21 and FY2021-22'))
        self.assertEqual(o.numeric_tokens('Q1 FY27 18.0%'), {'fy:2027', '18.0'})
        self.assertNotIn('forecast presented as certain', o.grounding_errors('Will customers pay on time?', 'Management expects customers to pay on time.'))

    def test_period_binding_and_reversed_direction_rejected(self):
        sources, _ = o.ingest(PACK, dt.date(2026, 9, 23))
        o.resolve_identity(sources, 'SRVCABLE')
        catalog = o.evidence_catalog(sources)
        margin_quote = next(e['quote'] for e in catalog if e['source'] == 'S3' and '| EBITDA margin |' in e['quote'])
        copper_quote = next(e['quote'] for e in catalog if e['source'] == 'S3' and 'sharp rise in copper' in e['quote'])
        self.assertIn('table value does not match claimed reporting period', o.grounding_errors('Q1 FY27 EBITDA margin was 12.9%.', margin_quote))
        self.assertIn('unsupported direction of change', o.grounding_errors('Copper prices fell sharply during the quarter.', copper_quote))
        margin = o.excerpt_display(next(s for s in sources if s.id == 'S3'), margin_quote)
        self.assertNotIn('(₹ crore)', margin)

    def test_actual_keyless_http_gateway_and_failure_fallback(self):
        received = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received.append((self.path, self.headers.get('Authorization'), json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                payload = json.dumps({'choices': [{'message': {'content': '{}'}, 'finish_reason': 'stop'}]}).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            def log_message(self, *unused):
                pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {
                'OPENAI_BASE_URL': f'http://127.0.0.1:{server.server_port}/v1',
                'OPENAI_MODEL': 'test-proxy-model',
            }, clear=True):
                args = o.parser().parse_args(['SRVCABLE', str(PACK), '--provider', 'openai', '--env-file', str(Path(temp)/'none'), '--output', str(Path(temp)/'brief.md'), '--audit', str(Path(temp)/'audit.json')])
                audit, _ = o.run(args)
                self.assertEqual(audit['mode'], 'offline')
                self.assertIn('Model validation failed', audit['fallback_reason'])
            self.assertEqual(received[0][0], '/v1/chat/completions')
            self.assertIsNone(received[0][1])
            self.assertEqual(received[0][2]['model'], 'test-proxy-model')
            self.assertNotIn('tools', received[0][2])
        finally:
            server.server_close()
            thread.join(timeout=2)


if __name__ == '__main__':
    unittest.main()
