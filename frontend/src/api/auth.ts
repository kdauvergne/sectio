import axios from "axios";
import { api, API_URL } from "@/lib/api";
import { deleteTokens, saveTokens, getRefreshToken } from "@/lib/tokens";
import type { Utilisateur } from "@/types/api";

/* POST /api/token/ identifiants vs tokens */

export async function connexion(
  email: string,
  password: string,
): Promise<void> {
  const response = await axios.post(`${API_URL}/token/`, {
    email,
    password: password,
  });
  saveTokens(response.data.access, response.data.refresh);
}

/* GET /api/me/ fiche utilisateur connecté */

export async function recupererProfilUtilisateur(): Promise<Utilisateur> {
  const response = await api.get<Utilisateur>("/me/");
  return response.data;
}

/* POST /api/token/blacklist/ invalide le refresh et clear le navigateur */
export async function deconnexion(): Promise<void> {
  const refreshToken = getRefreshToken();
  if (refreshToken) {
    try {
      await api.post("/token/blacklist/", { refresh: refreshToken });
    } catch {
      // Serveur injoignable ou refresh invalide
    }
  }
  deleteTokens();
}
