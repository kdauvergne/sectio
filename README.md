<div align="center">

# Sectio

**Dimensionnement de poteaux en béton armé selon l'Eurocode 2**

[![Moteur CI](https://github.com/kdauvergne/sectio/actions/workflows/moteur-ci.yml/badge.svg)](https://github.com/kdauvergne/sectio/actions/workflows/moteur-ci.yml)
![Status](https://img.shields.io/badge/status-en%20d%C3%A9veloppement-orange)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue)
![Poetry](https://img.shields.io/badge/dependency%20manager-Poetry-60A5FA)

🇫🇷 [Français](#français) · 🇬🇧 [English](#english)

</div>

---

## Français

> 🚧 **Projet en cours de développement.**

### Qu'est-ce que Sectio ?

Sectio est une application web de dimensionnement de **poteaux en béton armé bi-articulés**
(rotulé-rotulé), conforme à l'**Eurocode 2** — méthode simplifiée (FD P18-717, EC2 art. 5.8.5(51)).

À partir des charges (G, Q) et des hypothèses matériaux/géométriques d'un poteau, l'outil :

- vérifie le domaine d'application de la méthode simplifiée (et rejette explicitement un poteau hors périmètre, jamais de calcul silencieux) ;
- calcule la section d'acier nécessaire (As) et l'effort résistant (NRd) ;
- détermine le ferraillage réglementaire (armatures longitudinales et transversales, EC2 art. 9.5) ;
- vérifie la résistance au feu (méthode A, tableaux EC2-1-2 §5.3.2).

Sectio ne s'arrête pas au calcul : chaque poteau conserve l'historique de ses calculs et peut être
exporté en note PDF. L'ingénieur retrouve ainsi toutes ses notes de calcul centralisées au même
endroit, plutôt que dispersées entre plusieurs fichiers et logiciels.

Le projet est développé avec le soutien d'un ingénieur structure, qui valide les règles de calcul
et fournit les notes de référence utilisées pour la validation du moteur.

### Architecture

Monorepo organisé en trois modules indépendants :

```
sectio/
├── moteur/     # Moteur de calcul Python pur (zéro dépendance Django)
├── backend/    # API Django + DRF + PostgreSQL (en cours de démarrage)
└── frontend/   # React + TypeScript + Vite (à venir)
```

- **`moteur/`** — package Python autonome (`sectio_moteur`), avec ses propres tests et sa propre
  CI. Aucune dépendance à un framework web : importable et testable indépendamment, y compris pour
  une présentation en dehors du projet.
- **`backend/`** — expose le moteur via une API REST (Django + Django REST Framework), gère les
  utilisateurs, projets, bâtiments, niveaux et l'historique des calculs.
- **`frontend/`** — interface web (React + TypeScript), consomme l'API.

`moteur/` est la brique la plus avancée du projet ; `backend/` et `frontend/` démarrent tout juste.

### Pourquoi le code est en français

Le code source (noms de fonctions, variables, docstrings) est volontairement rédigé **en
français**, alors même que l'anglais est la convention habituelle en développement :

- le vocabulaire du projet est **normatif**, tiré de textes eux-mêmes rédigés en français (FD
  P18-717, transposition française de l'Eurocode 2) — traduire ces termes en anglais (`enrobage`,
  `ferraillage`, `poteau bi-articulé`...) obligerait à choisir des équivalents approximatifs, avec
  un vrai risque d'ambiguïté ou de contresens sur des notions réglementaires précises ;
- garder le code au plus près du vocabulaire de la norme facilite la relecture croisée entre le
  code et les textes réglementaires (EC2, guides Arche) qui, eux, resteront toujours en français ;
- c'est un choix délibéré de cohérence du domaine, pas une limite.

### Méthode de calcul

Méthode simplifiée EC2 (FD P18-717, art. 5.8.5(51)), sections rectangulaires et circulaires,
compression centrée. Le domaine d'application (élancement, résistances, enrobage...) est vérifié
explicitement avant tout calcul ; un poteau hors périmètre est rejeté avec la liste des conditions
violées, plutôt que de produire un résultat silencieusement incorrect.

Le moteur est validé par comparaison avec des notes de calcul de référence produites avec **Arche
Poteau (Graitec)**, avec un écart inférieur à 0,01 % sur l'effort résistant NRd sur les cas testés.

### Stack technique

| Domaine          | Choix                                                                                     |
| ---------------- | ----------------------------------------------------------------------------------------- |
| Moteur de calcul | Python 3.12+, Poetry, pytest, Ruff (lint + format)                                        |
| Backend          | Django, Django REST Framework, PostgreSQL, JWT (djangorestframework-simplejwt)            |
| Frontend         | React, TypeScript, Vite, Tailwind CSS, TanStack Query, React Hook Form, Zod, React Router |
| Export           | WeasyPrint (notes de calcul PDF)                                                          |
| CI/CD            | GitHub Actions, Docker                                                                    |

### Démarrer avec le moteur

```bash
cd moteur
poetry install --with dev

# Tests
poetry run pytest

# Lint et formatage (Ruff)
poetry run ruff check .
poetry run ruff format --check .
```

La CI (`.github/workflows/moteur-ci.yml`) exécute ces mêmes vérifications sur Python 3.12, 3.13 et
3.14 à chaque modification du dossier `moteur/`.

### État d'avancement

- Moteur de calcul : méthode simplifiée (flambement), choix des armatures, module feu — validés
  sur cas de référence Arche.
- Backend Django : modèle de données figé (MCD/MLD), implémentation en cours.
- Frontend : maquettes et développement à venir.

---

## English

> 🚧 **Currently under development.**

### What is Sectio?

Sectio is a web application for the structural design of **reinforced concrete
columns**, compliant with **Eurocode 2** — simplified method (FD P18-717, EC2 art. 5.8.5(51)).

Given the loads (G, Q) and a column's material/geometric assumptions, the tool:

- checks whether the simplified method actually applies (and explicitly rejects a column outside
  its scope, rather than computing a silently wrong result);
- computes the required steel area (As) and the resisting axial force (NRd);
- determines the regulatory reinforcement layout (longitudinal and transverse rebar, EC2 art. 9.5);
- checks fire resistance (Method A, EC2-1-2 §5.3.2 tables).

Sectio isn't just a calculator: every column keeps a history of its calculations, each exportable
as a PDF note. The engineer ends up with all reference calculation notes centralized in one place,
instead of scattered across multiple files and tools.

The project is developed with the support of a structural engineer, who validates the calculation
rules and provides the reference notes used to validate the engine.

### Architecture

A monorepo split into three independent modules:

```
sectio/
├── moteur/     # Pure Python calculation engine (zero Django dependency)
├── backend/    # Django + DRF + PostgreSQL API (early stage)
└── frontend/   # React + TypeScript + Vite (upcoming)
```

- **`moteur/`** — standalone Python package (`sectio_moteur`), with its own tests and its own CI.
  No dependency on any web framework: it can be imported and tested independently, including for
  demonstration purposes outside the main project.
- **`backend/`** — exposes the engine through a REST API (Django + Django REST Framework), and
  manages users, projects, buildings, levels and calculation history.
- **`frontend/`** — web interface (React + TypeScript), consumes the API.

`moteur/` is the most advanced part of the project; `backend/` and `frontend/` are just getting
started.

### Why the code is written in French

The source code (function names, variables, docstrings) is deliberately written **in French**,
even though English is the usual convention in software development:

- the domain vocabulary is **normative**, drawn from texts that are themselves written in French
  (FD P18-717, the French national application document for Eurocode 2) — translating these terms
  into English (`enrobage`, `ferraillage`, `poteau bi-articulé`...) would mean picking approximate
  equivalents, with a real risk of ambiguity or mistranslation on precise regulatory concepts;
- keeping the code close to the standard's own vocabulary makes it easier to cross-check the code
  against the regulatory texts (EC2, Arche guides), which will always stay in French;
- it's a deliberate choice driven by domain consistency, not a limitation.

### Calculation method

EC2 simplified method (FD P18-717, art. 5.8.5(51)), for rectangular and circular sections under
centered compression. The method's domain of applicability (slenderness, material strengths,
concrete cover...) is checked explicitly before any calculation; a column outside that scope is
rejected with the list of violated conditions, rather than silently producing an incorrect result.

The engine is validated against reference calculation notes produced with **Arche Poteau
(Graitec)**, with less than 0.01% deviation on the resisting force NRd on the tested cases.

### Tech stack

| Area               | Choice                                                                                    |
| ------------------ | ----------------------------------------------------------------------------------------- |
| Calculation engine | Python 3.12+, Poetry, pytest, Ruff (lint + format)                                        |
| Backend            | Django, Django REST Framework, PostgreSQL, JWT (djangorestframework-simplejwt)            |
| Frontend           | React, TypeScript, Vite, Tailwind CSS, TanStack Query, React Hook Form, Zod, React Router |
| Export             | WeasyPrint (PDF calculation notes)                                                        |
| CI/CD              | GitHub Actions, Docker                                                                    |

### Getting started with the engine

```bash
cd moteur
poetry install --with dev

# Tests
poetry run pytest

# Lint and formatting (Ruff)
poetry run ruff check .
poetry run ruff format --check .
```

CI (`.github/workflows/moteur-ci.yml`) runs the same checks on Python 3.12, 3.13 and 3.14 on every
change to the `moteur/` directory.

### Current status

- Calculation engine: simplified method (buckling), rebar selection, fire module — validated
  against Arche reference cases.
- Django backend: data model finalized (MCD/MLD), implementation in progress.
- Frontend: mockups and development to come.
