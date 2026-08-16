/** Forme d'un projet renvoyé par l'API Django (ProjetSerializer). */
export type Projet = {
  id: number;
  nom: string;
  description: string;
  date_creation: string;
  membres: number[];
  fck: number;
  fyk: number;
  classe_exposition: string;
};

/** Forme d'un poteau renvoyé par l'API Django (PoteauSerializer). */
export type Poteau = {
  id: number;
  niveau: number;
  type_poteau: number | null;
  repere: string;
  type_section: "rectangulaire" | "circulaire";
  b: number | null;
  h: number | null;
  diametre: number | null;
  L0: number;
  d_prime: number;
  G: number;
  Q: number;
  taux_travail_min: number;
  duree_resistance_feu: string;
  expose_un_seul_cote: boolean;
  fck: number;
  fyk: number;
  classe_exposition: string;
};

/** Enveloppe de pagination renvoyée par DjangoRestFramework */
export type Response<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

/** Utilisateur connecté, renvoyé par GET /api/me/. */
export type Utilisateur = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
};

export type NouvelUtilisateur = {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
};

/** POST /api/poteaux/ (création en lot) */
export type NouveauPoteau = {
  niveau: number;
  repere: string;
  type_section: "rectangulaire" | "circulaire";
  b: number | null;
  h: number | null;
  diametre: number | null;
  L0: number;
  d_prime: number;
  G: number;
  Q: number;
};
