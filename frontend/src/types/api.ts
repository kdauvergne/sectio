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
