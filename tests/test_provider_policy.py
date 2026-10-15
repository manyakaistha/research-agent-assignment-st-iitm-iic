import os
import unittest
from unittest.mock import patch

import orchestrator as o


class ProviderPolicyTests(unittest.TestCase):
    def config(self, ticker='SRVCABLE', *options):
        return o.route(o.parser().parse_args([ticker, 'unused-docs', *options]))

    def test_workflow_defaults_override_other_configured_providers(self):
        env = {'GROQ_API_KEY': 'groq-test', 'GEMINI_API_KEY': 'gemini-test',
               'OPENAI_API_KEY': 'openai-test', 'OPENAI_BASE_URL': 'https://gateway.example/v1'}
        with patch.dict(os.environ, env, clear=True):
            config = self.config()
            self.assertEqual(config['provider'], 'groq')
            self.assertEqual(config['model'], 'openai/gpt-oss-120b')
            config = self.config('WIPRO', '--live-data')
            self.assertEqual(config['provider'], 'gemini')
            self.assertEqual(config['model'], 'gemini-2.5-flash')

    def test_workflow_missing_key_never_switches_to_another_provider(self):
        for env in ({}, {'OPENAI_API_KEY': 'openai-test'},
                    {'GEMINI_API_KEY': 'gemini-test', 'OPENAI_BASE_URL': 'https://gateway.example/v1'}):
            with self.subTest(workflow='local', configured=tuple(env)), patch.dict(os.environ, env, clear=True):
                self.assertEqual(self.config()['provider'], 'offline')
        for env in ({}, {'OPENAI_API_KEY': 'openai-test', 'GROQ_API_KEY': 'groq-test'}):
            with self.subTest(workflow='live', configured=tuple(env)), patch.dict(os.environ, env, clear=True):
                self.assertEqual(self.config('WIPRO', '--live-data')['provider'], 'offline')

    def test_explicit_provider_overrides_workflow_including_offline(self):
        with patch.dict(os.environ, {}, clear=True):
            for ticker, options in (('SRVCABLE', []), ('WIPRO', ['--live-data'])):
                for provider in ('offline', 'groq', 'gemini', 'openai'):
                    with self.subTest(ticker=ticker, provider=provider):
                        self.assertEqual(self.config(ticker, *options, '--provider', provider)['provider'], provider)

    def test_provider_configuration_and_google_key_alias_are_preserved(self):
        env = {'GROQ_API_KEY': 'groq-test', 'GROQ_MODEL': 'groq-model',
               'GOOGLE_API_KEY': 'google-test', 'GEMINI_MODEL': 'gemini-model',
               'GEMINI_BASE_URL': 'https://gemini-gateway.example/v1'}
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(self.config()['model'], 'groq-model')
            config = self.config('WIPRO', '--live-data')
            self.assertEqual(config['model'], 'gemini-model')
            self.assertEqual(config['base_url'], env['GEMINI_BASE_URL'])
            self.assertEqual(config['key'], env['GOOGLE_API_KEY'])
            config = self.config('SRVCABLE', '--model', 'custom', '--base-url', 'http://localhost:8000/v1')
            self.assertEqual(config['model'], 'custom')
            self.assertEqual(config['base_url'], 'http://localhost:8000/v1')

    def test_other_local_tickers_retain_existing_auto_priority(self):
        for env, expected in (({}, 'offline'), ({'GROQ_API_KEY': 'g'}, 'groq'),
                              ({'GROQ_API_KEY': 'g', 'GEMINI_API_KEY': 'm'}, 'gemini'),
                              ({'GROQ_API_KEY': 'g', 'GEMINI_API_KEY': 'm', 'OPENAI_BASE_URL': 'http://localhost:8000/v1'}, 'openai')):
            with self.subTest(expected=expected), patch.dict(os.environ, env, clear=True):
                self.assertEqual(self.config('WIPRO')['provider'], expected)


if __name__ == '__main__':
    unittest.main()
