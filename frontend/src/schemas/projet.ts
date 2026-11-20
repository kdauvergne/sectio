import { z } from "zod";
import { CODES_EXPOSITION } from "@/lib/beton";

/** Bornes de fck : domaine d'application de la méthode simplifiée (FD P18-717). */
const FCK_MIN = 20;
const FCK_MAX = 50;

/** Hypothèses de calcul, communes au projet, au bâtiment et au niveau. */
export const schemaHypotheses = z.object({
  fck: z
    .number({ error: "Indiquez fck." })
    .min(
      FCK_MIN,
      "fck ne peut pas être inférieur à 20 MPa : en dessous, le béton sort du domaine d'application de la méthode EC2 utilisée par Sectio.",
    )
    .max(
      FCK_MAX,
      "fck ne peut pas dépasser 50 MPa : au-delà, les bétons à hautes performances sortent du domaine d'application de la méthode EC2 utilisée par Sectio.",
    ),
  fyk: z.number({ error: "Indiquez fyk." }).positive("fyk doit être positif."),
  classe_exposition: z.enum(CODES_EXPOSITION, {
    error: "Choisissez une classe d'exposition.",
  }),
});

function memeNom(a: string, b: string): boolean {
  return a.trim().toLowerCase() === b.trim().toLowerCase();
}

function champNom(messageVide: string, longueurMax: number) {
  return z
    .string()
    .trim()
    .min(1, messageVide)
    .max(longueurMax, `${longueurMax} caractères maximum.`);
}

export const schemaNouveauProjet = schemaHypotheses.extend({
  nom: champNom("Indiquez un nom de projet.", 150),
});

/** Le nom doit être libre parmi les bâtiments du projet (contrainte batiment_unique_par_projet). */
export function schemaNouveauBatiment(
  nomProjet: string,
  nomsExistants: string[],
) {
  return schemaHypotheses.extend({
    nom: champNom("Indiquez un nom de bâtiment.", 150).refine(
      (nom) => !nomsExistants.some((existant) => memeNom(existant, nom)),
      {
        error: (issue) =>
          `${nomProjet} contient déjà un bâtiment ${String(issue.input)}. Choisissez un autre nom pour distinguer les deux.`,
      },
    ),
  });
}

/** Le nom doit être libre parmi les niveaux du bâtiment (contrainte niveau_unique_par_batiment). */
export function schemaNouveauNiveau(
  nomBatiment: string,
  nomsExistants: string[],
) {
  return schemaHypotheses.extend({
    nom: champNom(
      "Indiquez un nom de niveau, par exemple RDC ou N+1.",
      100,
    ).refine(
      (nom) => !nomsExistants.some((existant) => memeNom(existant, nom)),
      {
        error: (issue) =>
          `${nomBatiment} contient déjà un niveau ${String(issue.input)}. Choisissez un autre nom pour distinguer les deux.`,
      },
    ),
  });
}
