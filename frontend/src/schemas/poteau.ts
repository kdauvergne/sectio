import { z } from "zod";

export const schemaPoteau = z
  .object({
    repere: z
      .string()
      .trim()
      .min(1, "Le repère est obligatoire")
      .max(8, "8 caractères maximum"),
    type_section: z.enum(["rectangulaire", "circulaire"]),
    b: z.number().positive("Doit être positif").nullable(),
    h: z.number().positive("Doit être positif").nullable(),
    diametre: z.number().positive("Doit être positif").nullable(),
    L0: z.number().positive("Doit être positif"),
    d_prime: z.number().positive("Doit être positif"),
    G: z.number().nonnegative("Ne peut pas être négatif"),
    Q: z.number().nonnegative("Ne peut pas être négatif"),
  })
  .superRefine((valeurs, ctx) => {
    if (valeurs.type_section === "rectangulaire") {
      if (valeurs.b === null) {
        ctx.addIssue({
          code: "custom",
          path: ["b"],
          message: "b est obligatoire",
        });
      }
      if (valeurs.h === null) {
        ctx.addIssue({
          code: "custom",
          path: ["h"],
          message: "h est obligatoire",
        });
      }
    } else if (valeurs.diametre === null) {
      ctx.addIssue({
        code: "custom",
        path: ["diametre"],
        message: "Le diamètre est obligatoire",
      });
    }
  });

export type SaisiePoteau = z.infer<typeof schemaPoteau>;

export const schemaSaisieNiveau = z
  .object({
    poteaux: z.array(schemaPoteau).min(1, "Ajoutez au moins un poteau"),
  })
  .superRefine((valeurs, ctx) => {
    const reperesVus = new Set<string>();

    valeurs.poteaux.forEach((poteau, index) => {
      if (reperesVus.has(poteau.repere)) {
        ctx.addIssue({
          code: "custom",
          path: ["poteaux", index, "repere"],
          message: "Ce repère est déjà utilisé",
        });
      } else {
        reperesVus.add(poteau.repere);
      }
    });
  });

export type SaisieNiveau = z.infer<typeof schemaSaisieNiveau>;
