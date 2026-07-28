Sectio - 🚧 Projet en cours de développement — le moteur de calcul est la brique actuellement en chantier.

Application web de dimensionnement de poteaux en béton armé bi-articulés (rotulé-rotulé), conforme à l'Eurocode 2 — méthode simplifiée (FD P18-717, EC2 art. 5.8.5(51)).

Objectif :

À partir des charges (G, Q) et des hypothèses matériaux/géométriques d'un poteau, l'outil :

- vérifie le domaine d'application de la méthode simplifiée,
- calcule la section d'acier nécessaire (As) et la force portante (NRd),
- détermine le ferraillage réglementaire (armatures longitudinales et transversales, EC2 art. 9.5),
- vérifie la résistance au feu (méthode A, tableaux EC2-1-2 §5.3.2).

Le dossier moteur/ est autonome : ses propres tests, sa propre CI, importable et testable sans base de données ni framework web.
