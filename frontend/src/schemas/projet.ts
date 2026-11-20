import { z } from "zod";
import { CODES_EXPOSITION } from "@/lib/beton";

/** Bornes de fck : domaine d'application de la méthode simplifiée (FD P18-717). */
const FCK_MIN = 20;
const FCK_MAX = 50;

export const schemaNouveauProjet = z.object({
  nom: z
    .string()
    .trim()
    .min(1, "Indiquez un nom de projet.")
    .max(150, "150 caractères maximum."),
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
