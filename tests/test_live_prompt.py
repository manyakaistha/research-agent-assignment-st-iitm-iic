import copy
import datetime as dt
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import orchestrator as o
from live_sources import normalize_wipro_html

ROOT = Path(__file__).resolve().parents[1]
SENTINEL = 'The supplied evidence does not establish a supported conclusion for this section.'


class LivePromptTests(unittest.TestCase):
    def sections(self, item):
        return {heading: [copy.deepcopy(item)] for heading in o.HEADINGS}

    def test_only_exact_empty_evidence_sentinel_is_allowed(self):
        item = {'text': SENTINEL, 'citations': [], 'evidence': []}
        self.assertEqual(o.validate(self.sections(item), [], [], '', model=True), [])
        for changed in (
                {'text': 'Revenue increased.', 'citations': [], 'evidence': []},
                {'text': SENTINEL + ' Revenue increased.', 'citations': [], 'evidence': []},
                {'text': SENTINEL, 'citations': []},
                {'text': SENTINEL, 'citations': [], 'evidence': ['S1:E2']},
                {'text': SENTINEL, 'citations': [], 'evidence': {}},
                {'text': SENTINEL, 'citations': 'S1', 'evidence': []}):
            with self.subTest(item=changed):
                self.assertTrue(o.validate(self.sections(changed), [], [], '', model=True))

    def test_factual_evidence_strings_still_rejected(self):
        source = o.Source('S1', 'a.md', 'Company', 'https://example.com/release/', '2026-10-15',
                          'official', '', 'Revenue was INR 100 million.', status='included')
        item = {'text': 'Revenue was INR 100 million.', 'citations': ['S1'], 'evidence': ['S1:E1']}
        self.assertIn('invalid evidence quote', o.validate(self.sections(item), [source], [], '', model=True))

    def test_run_selects_live_prompt_only_for_live_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / 'docs'; docs.mkdir()
            raw = (ROOT / 'tests/fixtures/wipro_release.html').read_text()
            markdown, _ = normalize_wipro_html(raw, 'https://www.wipro.com/newsroom/press-releases/2026/results/')
            (docs / 'release.md').write_text(markdown)
            for live in (False, True):
                args = o.parser().parse_args(['WIPRO', str(docs), '--provider', 'offline', '--as-of', '2026-10-16',
                         '--audit', str(root / ('live.json' if live else 'local.json')),
                         '--output', str(root / ('live.md' if live else 'local.md')), '--env-file', str(root / 'none')]
                         + (['--live-data'] if live else []))
                with patch.object(o, 'retrieve_live', return_value=([], [])):
                    audit = o.run(args)
                import json
                audit = json.loads(Path(args.audit).read_text())
                expected = (ROOT / ('live_system_prompt.md' if live else 'system_prompt.md')).read_text() + '\nReview policy: ' + o.REVIEWS[args.review]
                actual = Path(audit['run_dir'], 'writer_system_prompt.md').read_text()
                self.assertEqual(actual, expected)
                self.assertEqual(audit['prompt_sha256'], o.sha(expected))


if __name__ == '__main__':
    unittest.main()
