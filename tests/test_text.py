import unittest

from telegram_llm_bot.utils.text import chunk_text


class TestText(unittest.TestCase):
    def test_chunk_text_splits_long_value(self) -> None:
        text = "a" * 9000
        chunks = chunk_text(text, chunk_size=4000)

        self.assertEqual(len(chunks), 3)
        self.assertEqual(len(chunks[0]), 4000)
        self.assertEqual(len(chunks[1]), 4000)
        self.assertEqual(len(chunks[2]), 1000)


if __name__ == "__main__":
    unittest.main()
