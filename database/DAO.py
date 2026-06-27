from database.DB_connect import DBConnect
from model.genre import Genre
from model.artist import Artist
from dataclasses import dataclass


# Struttura meccanica fissa per trasportare i dati dell'arco al Model
@dataclass
class Connessione:
    id1: int
    id2: int


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def get_all_genres():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM genre"
        cursor.execute(query)
        for row in cursor:
            result.append(Genre(row["GenreId"], row["Name"]))
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_nodi(genre_id):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT DISTINCT a.ArtistId, a.Name
            FROM artist a, album al, track t
            WHERE a.ArtistId = al.ArtistId 
              AND al.AlbumId = t.AlbumId
              AND t.GenreId = %s
        """
        cursor.execute(query, (genre_id,))
        for row in cursor:
            result.append(Artist(row["ArtistId"], row["Name"]))
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_popolarita_artisti(genre_id):
        """Calcola la popolarità degli artisti sulle vendite interne al genere richiesto."""
        conn = DBConnect.get_connection()
        result = {}
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT al.ArtistId, COUNT(il.InvoiceLineId) as popolarita
            FROM invoiceline il, track t, album al
            WHERE il.TrackId = t.TrackId 
              AND t.AlbumId = al.AlbumId
              AND t.GenreId = %s
            GROUP BY al.ArtistId
        """
        cursor.execute(query, (genre_id,))
        for row in cursor:
            result[int(row["ArtistId"])] = int(row["popolarita"])
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def get_interazioni_archi(genre_id):
        """
        PATTERN UNIVERSALE: Unisce due tabelle virtuali di relazioni uniche Cliente-Artista
        filtrate per genere, accertando il cliente comune e applicando lo scudo '<'.
        """
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)

        # Questa query unisce in SQL le combinazioni esatte evitando prodotti cartesiani esplosivi
        query = """
            SELECT c1.ArtistId AS id1, c2.ArtistId AS id2
            FROM (
                SELECT DISTINCT i.CustomerId, al.ArtistId
                FROM invoice i, invoiceline il, track t, album al
                WHERE i.InvoiceId = il.InvoiceId 
                  AND il.TrackId = t.TrackId 
                  AND t.AlbumId = al.AlbumId
                  AND t.GenreId = %s
            ) c1, (
                SELECT DISTINCT i.CustomerId, al.ArtistId
                FROM invoice i, invoiceline il, track t, album al
                WHERE i.InvoiceId = il.InvoiceId 
                  AND il.TrackId = t.TrackId 
                  AND t.AlbumId = al.AlbumId
                  AND t.GenreId = %s
            ) c2
            WHERE c1.CustomerId = c2.CustomerId
              AND c1.ArtistId < c2.ArtistId -- Scudo universale anti-duplicato
        """

        cursor.execute(query, (genre_id, genre_id))
        for row in cursor:
            # Impacchettamento pulito e standardizzato dentro l'oggetto Connessione
            result.append(Connessione(id1=int(row["id1"]), id2=int(row["id2"])))

        cursor.close()
        conn.close()
        return result