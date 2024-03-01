from dataclasses import dataclass


@dataclass
class User:
    username: str = None
    name: str = None
    carma: int = 0

    def __iadd__(self, other: int):
        self.carma += other
        return self

    def __str__(self):
        return f"{self.name if self.name else self.username} ({self.carma})"

    def __hash__(self):
        return hash(self.username or "" + self.name or "")


