from unittest import TestCase

from carma_bot.handlers import Handlers


class TestChatCounter(TestCase):
    def test_counter_simple(self):
        target = ["спс", "спасибо", "благодарю", "thank you", "thanks", "от души", "по братски"]
        self.assertTrue(Handlers._acceptable(target, "Спасибо!"))
        self.assertTrue(Handlers._acceptable(target, "Спасибо !"))
        self.assertTrue(Handlers._acceptable(target, "от души."))
        self.assertTrue(Handlers._acceptable(target, "от души )"))
        self.assertTrue(Handlers._acceptable(target, "🕴от души🕴"))


class TestHandlers(TestCase):
    def test_parse_mentions(self):
        self.assertEqual(Handlers.parse_mentions("@qwe,@asd"), ["qwe", "asd"])
        self.assertEqual(Handlers.parse_mentions("@qwe asdvqefr grrg\nas"), ["qwe"])
        self.assertEqual(Handlers.parse_mentions("@qwe,@asd, @ewg"), ["qwe", "asd", "ewg"])
        self.assertEqual(Handlers.parse_mentions("@qwe asdvqefr grrg\n@ddd, @as, 123"), ["qwe", "ddd", "as"])
