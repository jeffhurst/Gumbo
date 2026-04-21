import os
import unittest

from telegram_llm_bot.config.settings import SettingsError, load_settings


class TestSettings(unittest.TestCase):
    def setUp(self) -> None:
        self._original = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._original)

    def test_load_settings_defaults(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "token"
        os.environ.pop("OLLAMA_BASE_URL", None)
        os.environ.pop("OLLAMA_API_KEY", None)
        os.environ.pop("OLLAMA_MODEL", None)
        os.environ.pop("OLLAMA_TEMPERATURE", None)
        os.environ.pop("MAX_HISTORY_MESSAGES", None)

        settings = load_settings()

        self.assertEqual(settings.ollama_base_url, "http://localhost:11434")
        self.assertEqual(settings.ollama_api_key, "ollama")
        self.assertEqual(settings.ollama_model, "llama3.2")
        self.assertEqual(settings.temperature, 0.4)
        self.assertEqual(settings.max_history_messages, 12)

    def test_load_settings_validates_temperature(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "token"
        os.environ["OLLAMA_TEMPERATURE"] = "9"

        with self.assertRaises(SettingsError):
            load_settings()


if __name__ == "__main__":
    unittest.main()
