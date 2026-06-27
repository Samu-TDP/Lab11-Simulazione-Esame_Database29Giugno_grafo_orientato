from dataclasses import dataclass

@dataclass
class Genre:
    GenreId: int
    Name: str

    def __str__(self):
        return self.Name