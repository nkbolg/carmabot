import os
from unittest import TestCase

from carma_bot.handlers import CarmaStorage


class TestCarmaStorage(TestCase):
    TMP_STORAGE = 'storage.tmp'

    def setUp(self) -> None:
        if os.path.exists(self.TMP_STORAGE):
            os.remove(self.TMP_STORAGE)

        self.cs = CarmaStorage(self.TMP_STORAGE)

    def tearDown(self) -> None:
        os.remove(self.TMP_STORAGE)

    def test_inc(self):
        self.cs.conditional_emplace(chat_id=1, name='Вася', user_id=10500, username='vasya')
        self.assertEqual(self.cs[('vasya', 1)].carma, 0)
        self.cs.inc(key=(10500, 1))
        self.assertEqual(self.cs[('vasya', 1)].carma, 1)

    def test_only_username(self):
        self.cs.conditional_emplace(chat_id=2, username='vasya')
        self.assertEqual(self.cs[('vasya', 2)].carma, 0)
        self.cs.conditional_emplace(chat_id=2, username='vasya', name='Вася', user_id=10500)
        self.cs.inc(key=(10500, 2))
        self.assertEqual(self.cs[(10500, 2)].carma, 1)
