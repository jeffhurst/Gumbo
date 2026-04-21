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
        os.environ["OPENAI_API_KEY"] = "key"
        os.environ.pop("OPENAI_MODEL", None)
        os.environ.pop("OPENAI_TEMPERATURE", None)
        os.environ.pop("MAX_HISTORY_MESSAGES", None)

        settings = load_settings()

        self.assertEqual(settings.openai_model, "gpt-4.1-mini")
        self.assertEqual(settings.temperature, 0.4)
        self.assertEqual(settings.max_history_messages, 12)

    def test_load_settings_validates_temperature(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "token"
        os.environ["OPENAI_API_KEY"] = "key"
        os.environ["OPENAI_TEMPERATURE"] = "9"

        with self.assertRaises(SettingsError):
            load_settings()


if __name__ == "__main__":
    unittest.main()
