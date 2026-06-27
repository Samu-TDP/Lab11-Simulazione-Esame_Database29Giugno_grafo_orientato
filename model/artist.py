from dataclasses import dataclass

@dataclass
class Artist:
    ArtistId: int
    Name: str

    # ==========================================
    # REGOLE D'ORO PER I NODI DEL GRAFO
    # ==========================================
    def __eq__(self, other):
        return self.ArtistId == other.ArtistId

    def __hash__(self):
        return hash(self.ArtistId)

    def __str__(self):
        return self.Name