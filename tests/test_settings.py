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
        os.environ.pop("OLLAMA_MODEL", None)
        os.environ.pop("OLLAMA_TEMPERATURE", None)
        os.environ.pop("MAX_HISTORY_MESSAGES", None)
        os.environ.pop("TELEGRAM_BOOT_CHAT_ID", None)

        settings = load_settings()

        self.assertEqual(settings.ollama_base_url, "http://localhost:11434")
        self.assertEqual(settings.ollama_model, "llama3.2")
        self.assertEqual(settings.temperature, 0.4)
        self.assertEqual(settings.max_history_messages, 12)
        self.assertIsNone(settings.telegram_boot_chat_id)

    def test_load_settings_validates_temperature(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "token"
        os.environ["OLLAMA_TEMPERATURE"] = "9"

        with self.assertRaises(SettingsError):
            load_settings()

    def test_load_settings_parses_boot_chat_id(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "token"
        os.environ["TELEGRAM_BOOT_CHAT_ID"] = "-1001234567890"

        settings = load_settings()

        self.assertEqual(settings.telegram_boot_chat_id, -1001234567890)


if __name__ == "__main__":
    unittest.main()
