import datetime
import pickle
import shelve
from typing import Union

from carma_bot.user_dataclass import User


class CarmaStorage:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.db = shelve.DbfilenameShelf(self.filename, writeback=True)
        if not self.db:
            self.db["all"] = {}
            self.db["last_month"] = {}
            self.db["current_month"] = datetime.datetime.utcnow().month
            self.db.sync()

    def inc(self, key: Union[tuple[str, int], tuple[int, int]]):
        self._flush_month(sync=False)

        self.db["all"][key] += 1
        self.db["last_month"][key] += 1
        self.db.sync()

    @staticmethod
    def _inner_emplace(
            key: Union[tuple[str, int], tuple[int, int]], user: User, data_dict
    ):
        if key not in data_dict:
            data_dict[key] = user

    def conditional_emplace(
            self,
            *,
            chat_id: int,
            name: str = None,
            user_id: int = None,
            username: str = None,
    ):
        self._flush_month(sync=False)

        username_key = username, chat_id
        userid_key = user_id, chat_id

        try:
            # if mentioned by username earlier but not mentioned by user_id
            if username is not None and user_id is not None:
                if username_key in self.db["all"] and userid_key not in self.db["all"]:
                    assert name is not None
                    self.db["all"][username_key].name = name
                    self.db["last_month"][username_key].name = name
                    self.db["all"][userid_key] = self.db["all"][username_key]
                    self.db["last_month"][userid_key] = self.db["last_month"][username_key]
                    return
        except KeyError:
            pass

        user_all = User(username, name)
        user_month = User(username, name)
        key = None

        if user_id is not None:
            self._inner_emplace(userid_key, user_all, self.db["all"])
            self._inner_emplace(userid_key, user_month, self.db["last_month"])
            key = userid_key

        if username is not None:
            self._inner_emplace(username_key, user_all, self.db["all"])
            self._inner_emplace(username_key, user_month, self.db["last_month"])
            key = username_key

        assert key is not None

        self.db.sync()

        return key

    def __getitem__(self, key: Union[tuple[str, int], tuple[int, int]]):
        return self.db["all"][key]

    def formatted_list_all(self, chat_id: int) -> str:
        filtered = list({v for k, v in self.db["all"].items() if k[1] == chat_id and v.carma != 0})
        sorted_list = sorted(filtered, key=lambda x: x.carma, reverse=True)
        return "\n".join(map(str, sorted_list)) or "Пока тут пусто"

    def formatted_list_month(self, chat_id: int):
        filtered = list({v for k, v in self.db["last_month"].items() if k[1] == chat_id and v.carma != 0})
        sorted_list = sorted(filtered, key=lambda x: x.carma, reverse=True)
        return "\n".join(map(str, sorted_list)) or "Пока тут пусто"

    def _flush_month(self, sync):
        now_month = datetime.datetime.utcnow().month

        if now_month != self.db["current_month"]:
            assert now_month > self.db["current_month"] or now_month == 1
            with open(f"{now_month-1}.pickle", 'wb') as f:
                pickle.dump(self.db["last_month"], f)
            self.db["last_month"] = {}
            self.db["current_month"] = now_month

        if sync:
            self.db.sync()
