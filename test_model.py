from database.DAO import DAO
from model.model import Model


def cerca_genere_per_nome(nome_genere):
    """
    Funzione di servizio per trovare il GenreId partendo dal nome del genere.

    Perché serve?
    Nel Controller l'utente seleziona un genere dal dropdown.
    Qui, invece, non abbiamo la GUI.

    Quindi cerchiamo manualmente il genere tramite il DAO.

    Input:
        nome_genere: stringa, ad esempio "Rock"

    Output:
        oggetto Genre se trovato, altrimenti None
    """

    generi = DAO.get_all_genres()

    for genere in generi:
        if genere.Name == nome_genere:
            return genere

    return None


def stampa_lista_generi():
    """
    Test base del DAO.

    Serve per verificare se:
    - la connessione al database funziona;
    - la query get_all_genres() funziona;
    - la dataclass Genre viene costruita correttamente.
    """

    print("\n==============================")
    print("TEST DAO - LISTA GENERI")
    print("==============================")

    generi = DAO.get_all_genres()

    print(f"Numero generi trovati: {len(generi)}")

    for genere in generi:
        print(f"{genere.GenreId} - {genere.Name}")


def test_dao_su_genere(genre_id):
    """
    Test diretto del DAO per un certo genere.

    Qui non sto ancora usando il Model.
    Sto solo controllando se le query SQL estraggono dati sensati.

    Controllo:
    1. nodi estratti;
    2. popolarità artisti;
    3. archi grezzi.
    """

    print("\n==============================")
    print("TEST DAO - DATI PER GENERE")
    print("==============================")

    nodi = DAO.get_nodi(genre_id)
    print(f"Nodi estratti dal DAO: {len(nodi)}")

    print("\nPrimi 10 nodi:")
    for nodo in nodi[:10]:
        print(f"{nodo.ArtistId} - {nodo.Name}")

    popolarita = DAO.get_popolarita_artisti(genre_id)
    print(f"\nNumero artisti con popolarità calcolata: {len(popolarita)}")

    print("\nPrime 10 popolarità:")
    contatore = 0
    for artist_id, pop in popolarita.items():
        print(f"ArtistId {artist_id} -> popolarità {pop}")
        contatore += 1
        if contatore == 10:
            break

    archi = DAO.get_interazioni_archi(genre_id)
    print(f"\nArchi grezzi estratti dal DAO: {len(archi)}")

    print("\nPrimi 10 archi grezzi:")
    for arco in archi[:10]:
        print(f"{arco.id1} - {arco.id2}")


def test_model_creazione_grafo(genre_id):
    """
    Test del Model.

    Qui verifico se:
    - il grafo viene creato;
    - i nodi vengono aggiunti;
    - gli archi vengono orientati;
    - i pesi vengono calcolati;
    - le funzioni di dettaglio funzionano.
    """

    print("\n==============================")
    print("TEST MODEL - CREAZIONE GRAFO")
    print("==============================")

    model = Model()

    model.crea_grafo(genre_id)

    print(f"Numero nodi grafo: {model.get_num_nodi()}")
    print(f"Numero archi grafo: {model.get_num_archi()}")

    artista, influenza = model.get_artista_influente()

    print("\nArtista più influente:")
    if artista is not None:
        print(f"{artista} - influenza = {influenza}")
    else:
        print("Nessun artista trovato.")

    print("\nTop 5 archi:")

    top_edges = model.get_top_edges(5)

    for u, v, data in top_edges:
        peso = data["weight"]
        print(f"{u} -> {v} | peso = {peso}")

    return model


def test_ricorsione(model):
    """
    Test della ricorsione.

    Scelgo come nodo di partenza l'artista più influente,
    perché di solito ha archi uscenti e quindi permette di testare
    meglio il cammino.

    Se vuoi testare un artista specifico, puoi sostituire questa parte
    con una ricerca manuale dentro i nodi del grafo.
    """

    print("\n==============================")
    print("TEST MODEL - RICORSIONE")
    print("==============================")

    artista_start, influenza = model.get_artista_influente()

    if artista_start is None:
        print("Non posso testare la ricorsione: artista di partenza non trovato.")
        return

    print(f"Nodo di partenza scelto: {artista_start}")

    cammino = model.get_cammino_crescente(artista_start)

    if cammino is None or len(cammino) == 0:
        print("Nessun cammino trovato.")
        return

    print(f"Lunghezza cammino in nodi: {len(cammino)}")
    print(f"Lunghezza cammino in archi: {len(cammino) - 1}")

    print("\nCammino trovato:")

    for i in range(len(cammino)):
        print(cammino[i])

    print("\nDettaglio archi del cammino:")

    peso_totale = 0

    for i in range(len(cammino) - 1):
        u = cammino[i]
        v = cammino[i + 1]

        peso = model._grafo[u][v]["weight"]
        peso_totale += peso

        print(f"{u} -> {v} | peso = {peso}")

    print(f"\nPeso totale cammino: {peso_totale}")


if __name__ == "__main__":

    # ------------------------------------------------------------
    # PARAMETRO DI TEST
    # ------------------------------------------------------------
    #
    # Cambia qui il genere da testare.
    # Esempi possibili: "Rock", "Jazz", "Metal", "Latin".
    #
    # Questo simula la scelta che normalmente faresti dal dropdown.

    nome_genere_test = "Rock"

    # ------------------------------------------------------------
    # 1. Test lista generi
    # ------------------------------------------------------------

    stampa_lista_generi()

    # ------------------------------------------------------------
    # 2. Recupero GenreId dal nome
    # ------------------------------------------------------------

    genere = cerca_genere_per_nome(nome_genere_test)

    if genere is None:
        print(f"\nERRORE: genere '{nome_genere_test}' non trovato nel database.")
    else:
        print("\n==============================")
        print("GENERE SCELTO PER IL TEST")
        print("==============================")
        print(f"Genere scelto: {genere.GenreId} - {genere.Name}")

        # ------------------------------------------------------------
        # 3. Test DAO
        # ------------------------------------------------------------

        test_dao_su_genere(genere.GenreId)

        # ------------------------------------------------------------
        # 4. Test Model
        # ------------------------------------------------------------

        model = test_model_creazione_grafo(genere.GenreId)

        # ------------------------------------------------------------
        # 5. Test ricorsione
        # ------------------------------------------------------------

        test_ricorsione(model)