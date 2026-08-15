import { z } from "zod";

export const schemaConnexion = z.object({
  email: z.email("Adresse e-mail invalide."),
  password: z.string().min(1, "Le mot de passe est obligatoire."),
});

export type SaisieConnexion = z.infer<typeof schemaConnexion>;

export const schemaResetPwd = z.object({
  email: z.email("Adresse e-mail invalide."),
});

export type SaisieResetPwd = z.infer<typeof schemaResetPwd>;
