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

