import { api, publicApi } from "@/lib/api";
import type { Utilisateur } from "@/types/api";

/** POST /api/token/ */
export async function connexion(
  email: string,
  motDePasse: string,
): Promise<void> {
  await publicApi.post("/token/", { email, password: motDePasse });
}

/** GET /api/me/ */
export async function recupererMonCompte(): Promise<Utilisateur> {
  const reponse = await api.get<Utilisateur>("/me/");
  return reponse.data;
}

/** POST /api/deconnexion/ */
export async function deconnexion(): Promise<void> {
  try {
    await publicApi.post("/deconnexion/");
  } catch {
    // continue
  }
}

/** POST /api/mot-de-passe-oublie/ */
export async function demandeResetPwd(email: string): Promise<void> {
  await publicApi.post("/mot-de-passe-oublie/", { email });
}
