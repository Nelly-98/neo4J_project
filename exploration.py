#Nombre de correspondances par station
MATCH (s:Station)-[:COMPREND]->(sl:StationLigne)-[:CORRESPONDANCE]->(sl2:StationLigne)<-[:COMPREND]-(s)
RETURN s.nom_gare AS Station, count(distinct sl2) AS Correspondances;

#Nombre de stations à moins de deux kilomètres de LADEFENSE
MATCH (start:Station {nom_clean: "LADEFENSE"}), (stop:Station)
WHERE distance(point({x: start.x, y: start.y}), point({x: stop.x, y: stop.y})) < 2000
RETURN count(distinct stop) AS StationsProches;

#Temps pour aller en metro de LADEFENSE à CHATEAUDEVINCENNES
MATCH path=shortestPath((start:Station {nom_clean: "LADEFENSE"})-[:LIAISON*]->(end:Station {nom_clean: "CHATEAUDEVINCENNES"}))
WITH path, reduce(time = 0, r in relationships(path) | time + r.temps) AS TempsTotal
RETURN TempsTotal;

#Temps pour aller à pied de LADEFENSE à CHATEAUDEVINCENNES
MATCH (start:Station {nom_clean: "LADEFENSE"}), (end:Station {nom_clean: "CHATEAUDEVINCENNES"})
WITH distance(point({x: start.x, y: start.y}), point({x: end.x, y: end.y})) AS Distance
RETURN Distance / 1000 / 4 AS TempsHeures; #Vitesse de 4km/h

#Est-il plus rapide de faire un changement à SAINTLAZARE pour aller de MONTPARNASSEBIENVENUE à GABRIELPERI ?

#Nombre de stations dans un rayon de 10 stations par train autour de SAINTLAZARE
MATCH (start:Station {nom_clean: "SAINTLAZARE"})-[:LIAISON*1..10]->(stop:Station)
RETURN count(distinct stop) AS StationsDansRayon;

#Nombre de stations dans un rayon de 20 minutes par train autour de SAINTLAZARE
MATCH (start:Station {nom_clean: "SAINTLAZARE"})-[:LIAISON*]->(stop:Station)
WITH start, stop, sum(r.temps) AS TempsTotal
WHERE TempsTotal <= 20
RETURN count(distinct stop) AS StationsDansRayon20min;
