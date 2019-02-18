from dataclasses import dataclass


@dataclass()
class User:
    id: int
    first_name: str
    last_name: str

    def __repr__(self):
        return '%s %s' % (self.first_name, self.last_name)
