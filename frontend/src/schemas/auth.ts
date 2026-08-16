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

export const schemaMotDePasse = z
  .string()
  .min(12, { message: "Le mot de passe doit avoir au minimum 12 caractères." });

export const schemaNouveauMotDePasse = z
  .object({
    new_password: schemaMotDePasse,
    confirmPassword: z.string(),
  })
  .refine((data) => data.new_password === data.confirmPassword, {
    message: "Les mots de passe doivent être identiques",
    path: ["confirmPassword"],
  });
