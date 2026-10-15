"""Independent counterexamples; tests express desired safety behavior, not current behavior."""
import copy
import datetime as dt
from pathlib import Path
import shutil
import tempfile
import unittest
import orchestrator as o

PACK = Path(__file__).resolve().parents[1] / 'AI innovator assignment'

class IndependentReviewTests(unittest.TestCase):
    def sources(self):
        sources, _ = o.ingest(PACK, dt.date(2026,9,23))
        o.resolve_identity(sources, 'SRVCABLE')
        return sources

    def sections(self, claim, source):
        quote = 'Revenue from operations | 1,248 | 1,058 | +18.0%'
        return {h:[{'text':claim, 'citations':[source.id],
                    'evidence':[{'source':source.id,'quote':quote}]}] for h in o.HEADINGS}

    def test_false_claim_with_unrelated_exact_quote_rejected(self):
        sources = self.sources()
        source = next(s for s in sources if s.filename.startswith('ir_press_release'))
        sections = self.sections('The company has no exposure to copper prices.', source)
        self.assertTrue(o.validate(sections,sources,[],o.render(sections,sources,[]),model=True))

    def test_wrong_metric_and_negative_sign_rejected(self):
        sources = self.sources()
        source = next(s for s in sources if s.filename.startswith('ir_press_release'))
        sections = self.sections('Profit after tax was minus ₹1,248 crore.', source)
        self.assertTrue(o.validate(sections,sources,[],o.render(sections,sources,[]),model=True))

    def test_same_period_late_correction_detected(self):
        sources = self.sources()
        news = next(s for s in sources if s.filename.startswith('businessdaily'))
        news.published = '2026-09-09'
        conflicts, _ = o.detect_issues(sources)
        self.assertTrue(conflicts)

    def test_different_periods_not_called_conflict(self):
        sources = self.sources()
        news = next(s for s in sources if s.filename.startswith('businessdaily'))
        news.body = news.body.replace('April–June quarter','January–March quarter').replace("Q1 revenue", "Q4 revenue")
        conflicts, _ = o.detect_issues(sources)
        self.assertFalse(conflicts)

    def test_unrelated_company_mentions_target_is_excluded(self):
        sources = self.sources()
        news = next(s for s in sources if s.filename.startswith('nagpurcitytimes'))
        news.body += '\nThis company is unrelated to Sarvottam Cables Ltd.\n'
        o.resolve_identity(sources, 'SRVCABLE')
        self.assertEqual(news.status, 'excluded')

    def test_generated_run_artifacts_stay_outside_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root/'runs'
            shutil.copytree(PACK,docs)
            before = {str(p.relative_to(docs)) for p in docs.rglob('*')}
            args = o.parser().parse_args(['SRVCABLE',str(docs),'--provider','offline','--audit',str(root/'audit.json'),'--output',str(root/'brief.md'),'--env-file',str(root/'none')])
            o.run(args)
            self.assertEqual(before,{str(p.relative_to(docs)) for p in docs.rglob('*')})

if __name__ == '__main__':
    unittest.main()
