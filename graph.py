from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('', ''))

# Supprimer les données précédentes
print('Deleting previous data')

delete_query = '''
MATCH (n)
DETACH DELETE n
'''

with driver.session() as session:
    session.run(delete_query)

print('done')

# Insertion données des stations
print('Inserting Stations')
stations_query = '''
LOAD CSV WITH HEADERS FROM 'https://github.com/pauldechorgnat/cool-datasets/raw/master/ratp/stations.csv' AS row
MERGE (s:Station {nom_clean: row.nom_clean})
ON CREATE SET s.nom_gare = row.nom_gare, s.x = toFloat(row.x), s.y = toFloat(row.y), s.trafic = toInteger(row.Trafic), s.ville = row.Ville
WITH s, row
MERGE (l:Ligne {numero: toInteger(row.ligne)})
MERGE (s)-[:APPARTIENT_A]->(l);
'''

with driver.session() as session:
    session.run(stations_query)

print('done')

# Insertions données des liaisons
print('Inserting Liaisons')
liaisons_query = '''
LOAD CSV WITH HEADERS FROM 'https://github.com/pauldechorgnat/cool-datasets/raw/master/ratp/liaisons.csv' AS row
MATCH (startStation:Station {nom_clean: row.start}), (stopStation:Station {nom_clean: row.stop})
WITH startStation, stopStation, row
MATCH (ligne:Ligne {numero: toInteger(row.ligne)})
MERGE (startStation)-[:LIAISON {ligne: ligne.numero}]->(stopStation);
'''

with driver.session() as session:
    session.run(liaisons_query)

print('done')

#  relations entre stations pour les correspondances et liaisons à pied
print('Creating relationships')
queries = [
    '''
    MATCH (s1:Station)-[:APPARTIENT_A]->(l1:Ligne), (s2:Station)-[:APPARTIENT_A]->(l2:Ligne)
    WHERE s1.nom_clean = s2.nom_clean AND l1 <> l2
    MERGE (s1)-[:CORRESPONDANCE {temps: 4}]->(s2)
    ''',
    '''
    MATCH (s1:Station), (s2:Station)
    WHERE s1 <> s2 AND sqrt((s1.x - s2.x)^2 + (s1.y - s2.y)^2) < 1000
    MERGE (s1)-[:A_PIED]->(s2)
    '''
]
with driver.session() as session:
    for q in queries:
        print(q)
        session.run(q)
print('done')
