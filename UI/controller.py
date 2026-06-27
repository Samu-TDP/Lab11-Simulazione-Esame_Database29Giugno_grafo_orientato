import flet as ft
from database.DAO import DAO  # Importiamo il DAO per riempire la prima tendina


class Controller:
    def __init__(self, view, model):
        # Il Postino: collega l'interfaccia (View) al cervello (Model)
        self._view = view
        self._model = model

    # =========================================================================
    # FUNZIONI DI SUPPORTO (Riempimento Tendine)
    # =========================================================================

    def fillDDGenre(self):
        """
        Metodo chiamato automaticamente dalla View all'avvio dell'app.
        Serve a popolare la prima tendina con tutti i generi musicali.
        """
        # Chiediamo al DAO la lista dei generi
        generi = DAO.get_all_genres()

        # Svuotiamo eventuali vecchie opzioni per sicurezza
        self._view._ddGenre.options.clear()

        # Popoliamo la tendina: la chiave è l'ID (per il database), il testo è il Nome (per l'utente)
        for g in generi:
            self._view._ddGenre.options.append(ft.dropdown.Option(key=str(g.GenreId), text=g.Name))

        self._view.update_page()

    def fillDDArtist(self):
        """
        Metodo chiamato DOPO aver creato il grafo.
        Popola la seconda tendina solo con gli artisti validi e presenti nel grafo.
        """
        self._view._ddArtist.options.clear()

        # Recuperiamo i nodi direttamente dalla mappa del model
        artisti = self._model._idMap.values()

        for a in artisti:
            self._view._ddArtist.options.append(ft.dropdown.Option(key=str(a.ArtistId), text=a.Name))

        self._view.update_page()

    # =========================================================================
    # PUNTO 1: CREAZIONE GRAFO E STATISTICHE
    # =========================================================================

    def handleCreaGrafo(self, e):
        """Metodo meccanico a 5 step collegato al bottone 'Crea Grafo'."""

        # --- STEP 1: PULIZIA ---
        self._view.txt_result.controls.clear()

        # --- STEP 2: VALIDAZIONE DELL'INPUT ---
        genere_id_str = self._view._ddGenre.value

        # Controllo salvavita: l'utente ha selezionato qualcosa?
        if genere_id_str is None:
            self._view.create_alert("Attenzione: Selezionare un genere musicale dal menu a tendina.")
            return

        # Trasformiamo la stringa dell'ID in intero per passarlo al Model
        genere_id = int(genere_id_str)

        # --- STEP 3: DELEGA AL MODEL ---
        # Facciamo lavorare il cervello
        self._model.crea_grafo(genere_id)

        # Raccogliamo i risultati elaborati
        n_nodi = self._model.get_num_nodi()
        n_archi = self._model.get_num_archi()
        top_archi = self._model.get_top_edges(5)
        artista_influente, score_influente = self._model.get_artista_influente()

        # --- STEP 4: IMPAGINAZIONE DEI RISULTATI ---
        # 4a. Statistiche di base
        self._view.txt_result.controls.append(ft.Text("Grafo correttamente creato!", color="green", weight="bold"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {n_nodi}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {n_archi}"))

        # 4b. Artista più influente (con controllo di sicurezza)
        if artista_influente is not None:
            self._view.txt_result.controls.append(
                ft.Text(f"Artista più influente: {artista_influente.Name}, con influenza: {score_influente}",
                        color="blue", weight="bold")
            )

        # 4c. Stampa dei Top 5 Archi
        self._view.txt_result.controls.append(ft.Text("\nTop 5 archi (peso decrescente):", weight="bold"))
        for u, v, dati in top_archi:
            # dati è il dizionario degli attributi, ad es. {'weight': 150}
            self._view.txt_result.controls.append(
                ft.Text(f"{u.Name} -> {v.Name}: {dati['weight']}")
            )

        # FONDAMENTALE: Adesso che il grafo esiste, sblocco il Punto 2 riempiendo la seconda tendina!
        self.fillDDArtist()

        # --- STEP 5: AGGIORNAMENTO SCHERMO ---
        self._view.update_page()

    # =========================================================================
    # PUNTO 2: ALGORITMO RICORSIVO (Cammino crescente)
    # =========================================================================

    def handleCammino(self, e):
        """Metodo meccanico a 5 step collegato al bottone 'Trova Cammino'."""

        # --- STEP 1: PULIZIA ---
        self._view.txt_result.controls.clear()

        # --- STEP 2: VALIDAZIONE DELL'INPUT ---
        # 2a. Il grafo è stato creato? Se no, fermati e avvisa.
        if self._model.get_num_nodi() == 0:
            self._view.create_alert("Errore: Devi prima creare il grafo!")
            return

        # 2b. L'utente ha selezionato un artista?
        artista_id_str = self._view._ddArtist.value

        if artista_id_str is None:
            self._view.create_alert("Attenzione: Seleziona un artista dal menu a tendina.")
            return

        # 2c. Traduzione da stringa ID a Oggetto vero e proprio tramite la Mappa
        nodo_partenza = self._model._idMap.get(int(artista_id_str))

        if nodo_partenza is None:
            self._view.create_alert("Errore critico: Artista non trovato nel grafo.")
            return

        # --- STEP 3: DELEGA AL MODEL (Algoritmo) ---
        # Mettiamo un messaggio di attesa nel caso la ricerca sia lunga
        self._view.txt_result.controls.append(ft.Text(f"Ricerca in corso...", color="orange"))
        self._view.update_page()

        # Lancia il motore di ricorsione
        cammino_ottimo = self._model.get_cammino_crescente(nodo_partenza)

        # --- STEP 4: IMPAGINAZIONE DEI RISULTATI ---
        self._view.txt_result.controls.clear()  # Togliamo la scritta "Ricerca in corso..."

        # Controllo: Se la lista contiene solo 1 nodo (o 0), significa che non poteva muoversi da nessuna parte.
        if cammino_ottimo is None or len(cammino_ottimo) <= 1:
            self._view.txt_result.controls.append(
                ft.Text(f"Nessun cammino valido trovato a partire da {nodo_partenza.Name}.", color="red")
            )
        else:
            self._view.txt_result.controls.append(
                ft.Text(f"Cammino massimo trovato! Lunghezza: {len(cammino_ottimo)}", color="green", weight="bold")
            )

            # Stampiamo il cammino nodo per nodo, mostrando anche il peso per confermare che sia crescente
            self._view.txt_result.controls.append(ft.Text(f"1. {cammino_ottimo[0].Name}"))

            for i in range(1, len(cammino_ottimo)):
                # Recuperiamo il nodo precedente e l'attuale per risalire all'arco
                nodo_prec = cammino_ottimo[i - 1]
                nodo_corr = cammino_ottimo[i]

                # Leggiamo il peso dal grafo per stamparlo a video
                peso_arco = self._model._grafo[nodo_prec][nodo_corr]['weight']

                self._view.txt_result.controls.append(
                    ft.Text(f"{i + 1}. {nodo_corr.Name} (Peso attraversato: {peso_arco})")
                )

        # --- STEP 5: AGGIORNAMENTO SCHERMO ---
        self._view.update_page()