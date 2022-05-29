from unittest import TestCase

from yadro_management.handlers import ChatCounter


class TestChatCounter(TestCase):
    def test_counter_simple(self):
        cnt = ChatCounter()
        self.assertEqual(cnt.counter, 0)
        with cnt as counter:
            self.assertEqual(counter, 1)
            self.assertEqual(cnt.counter, 1)
        self.assertEqual(cnt.counter, 1)

    def test_exception(self):
        cnt = ChatCounter()
        try:
            with cnt as _:
                raise RuntimeError('test exception')
        except RuntimeError:
            pass
        finally:
            self.assertEqual(cnt.counter, 0)

