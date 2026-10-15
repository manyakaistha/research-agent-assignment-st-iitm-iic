"""Independent live financial-scope counterexamples, using saved source evidence."""
import unittest

import orchestrator as o


class LiveFinancialReviewTests(unittest.TestCase):
    def reject(self, claim, quote):
        source = o.Source('S1', 'live.md', 'Wipro official press release',
                          'https://www.wipro.com/newsroom/press-releases/2026/results/',
                          '2026-10-15', 'official company press release', '', quote,
                          trust='high', status='included')
        sections = {heading: [{'text': claim, 'citations': ['S1'],
                              'evidence': [{'id': 'S1:E1'}]}]
                    for heading in o.HEADINGS}
        self.assertTrue(o.validate(sections, [source], [],
                                   o.render(sections, [source], []), model=True))

    def test_unstated_consolidated_scope_is_rejected(self):
        self.reject("Wipro's consolidated gross revenue was ₹247.5 billion.",
                    'Gross revenue at ₹247.5 billion ($2,583.0 million [1] ), an increase of 1.1% QoQ and 9.1% YoY.')

    def test_gross_revenue_is_not_net_income(self):
        self.reject("Wipro's net income was ₹247.5 billion.",
                    'Gross revenue at ₹247.5 billion ($2,583.0 million [1] ), an increase of 1.1% QoQ and 9.1% YoY.')

    def test_constant_currency_growth_is_not_reported_growth(self):
        self.reject('Reported IT Services revenue increased 0.6% YoY.',
                    'Non-GAAP constant currency [2] IT Services segment revenue was flat sequentially and increase of 0.6% YoY.')

    def test_segment_margin_is_not_company_wide_margin(self):
        self.reject('Company-wide operating margin was 16.5%.',
                    'IT services operating margin [5] for Q2’27 was at 16.5%, up by 0.5% QoQ and down by 0.2% YoY.')


if __name__ == '__main__':
    unittest.main()
