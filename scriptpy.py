from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = ""
password = ""

class ItineraireCalculator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def calculer_itineraire(self, depart_x, depart_y, arrivee_x, arrivee_y):
        with self.driver.session() as session:
            result = session.write_transaction(self._calculer_itineraire_interne,
                                               depart_x, depart_y, arrivee_x, arrivee_y)
            for record in result:
                print(f"De {record['depart']} à {record['arrivee']} via {record['ligne']} - Temps Total: {record['tempsTotal']} minutes")

    @staticmethod
    def _calculer_itineraire_interne(tx, depart_x, depart_y, arrivee_x, arrivee_y):
        query = (
            '''
            MATCH (depart:Station), (arrivee:Station)
            WHERE distance(point(depart), point({x: $depart_x, y: $depart_y})) < 500 
              AND distance(point(arrivee), point({x: $arrivee_x, y: $arrivee_y})) < 500
            CALL apoc.algo.dijkstra(depart, arrivee, 'LIAISON|CORRESPONDANCE|A_PIED', 'temps') YIELD path, weight
            UNWIND nodes(path) AS station
            MATCH (station)-[:APPARTIENT_A]->(ligne:Ligne)
            RETURN station.nom_gare AS depart, arrivee.nom_gare AS arrivee, ligne.numero AS ligne, weight AS tempsTotal
            ORDER BY tempsTotal ASC LIMIT 1
            '''
        )
        return tx.run(query, depart_x=depart_x, depart_y=depart_y, arrivee_x=arrivee_x, arrivee_y=arrivee_y)



calculateur = ItineraireCalculator(uri, user, password)
try:
    calculateur.calculer_itineraire(2.3469, 48.8584, 2.295, 48.8738)
finally:
    calculateur.close()
