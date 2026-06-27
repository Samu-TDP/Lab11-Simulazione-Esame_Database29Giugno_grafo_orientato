import networkx as nx
from database.DAO import DAO


class Model:
    def __init__(self):
        self._grafo = nx.DiGraph()  # Grafo orientato d'esame
        self._idMap = {}
        self._best_path = []
        self._best_score = 0

    def crea_grafo(self, genre_id):
        # STEP 1: RESET DELLA MEMORIA RAM
        self._grafo.clear()
        self._idMap.clear()

        # STEP 2: AGGIUNTA DEI NODI ALLA MAPPA E AL GRAFO
        nodi = DAO.get_nodi(genre_id)
        for n in nodi:
            self._idMap[n.ArtistId] = n
        self._grafo.add_nodes_from(nodi)

        # STEP 3: RECUPERO STATISTICHE E ARCHI DAL DAO (Tramite la Dataclass)
        dizionario_popolarita = DAO.get_popolarita_artisti(genre_id)
        archi_dataclass = DAO.get_interazioni_archi(genre_id)

        # STEP 4: IL PATTERN GEOMETRICO FISSO IN RAM
        for edge in archi_dataclass:
            # Verifichiamo in tempo costante O(1) se entrambi gli ID fanno parte dei nostri nodi filtrati
            if edge.id1 in self._idMap and edge.id2 in self._idMap:
                nodo_A = self._idMap[edge.id1]
                nodo_B = self._idMap[edge.id2]

                pop_A = dizionario_popolarita.get(nodo_A.ArtistId, 0)
                pop_B = dizionario_popolarita.get(nodo_B.ArtistId, 0)

                # Il peso dell'arco è la somma delle rispettive popolarità
                peso_arco = pop_A + pop_B

                # BIAS DIREZIONALE MECCANICO (Risolve l'orientamento per ogni traccia possibile)
                if pop_A > pop_B:
                    self._grafo.add_edge(nodo_A, nodo_B, weight=peso_arco)
                elif pop_B > pop_A:
                    self._grafo.add_edge(nodo_B, nodo_A, weight=peso_arco)
                else:
                    # In caso di perfetta uguaglianza, la consegna impone la bidirezionalità
                    self._grafo.add_edge(nodo_A, nodo_B, weight=peso_arco)
                    self._grafo.add_edge(nodo_B, nodo_A, weight=peso_arco)

    # =========================================================================
    # METODI DI INTERROGAZIONE (Invariati e robusti)
    # =========================================================================
    def get_num_nodi(self):
        return self._grafo.number_of_nodes()

    def get_num_archi(self):
        return self._grafo.number_of_edges()

    def get_top_edges(self, n=5):
        tutti_archi = list(self._grafo.edges(data=True))
        tutti_archi.sort(key=lambda x: x[2]['weight'], reverse=True)
        return tutti_archi[:n]

    def get_artista_influente(self):
        if self._grafo.number_of_nodes() == 0:
            return None, 0
        best_artista = None
        best_influenza = float('-inf')

        for nodo in self._grafo.nodes():
            somma_uscenti = sum([dati['weight'] for u, v, dati in self._grafo.out_edges(nodo, data=True)])
            somma_entranti = sum([dati['weight'] for u, v, dati in self._grafo.in_edges(nodo, data=True)])
            influenza_attuale = somma_uscenti - somma_entranti

            if influenza_attuale > best_influenza:
                best_influenza = influenza_attuale
                best_artista = nodo
        return best_artista, best_influenza

    # =========================================================================
    # RICORSIONE BACKTRACKING PUNTO 2 (Invariata e pulita)
    # =========================================================================
    def get_cammino_crescente(self, nodo_partenza):
        self._best_path = []
        self._best_score = 0
        parziale = [nodo_partenza]
        self._ricorsione(parziale)
        return self._best_path

    def _ricorsione(self, parziale):
        if len(parziale) > self._best_score:
            self._best_score = len(parziale)
            self._best_path = list(parziale)

        ultimo_nodo = parziale[-1]
        candidati = self._grafo.successors(ultimo_nodo)

        for candidato in candidati:
            if candidato not in parziale:
                peso_nuovo_arco = self._grafo[ultimo_nodo][candidato]['weight']
                if len(parziale) == 1:
                    parziale.append(candidato)
                    self._ricorsione(parziale)
                    parziale.pop()
                else:
                    penultimo_nodo = parziale[-2]
                    peso_arco_precedente = self._grafo[penultimo_nodo][ultimo_nodo]['weight']
                    if peso_nuovo_arco > peso_arco_precedente:
                        parziale.append(candidato)
                        self._ricorsione(parziale)
                        parziale.pop()