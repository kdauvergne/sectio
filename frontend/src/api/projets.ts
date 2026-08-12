import { api } from "@/lib/api";
import type { Projet, Response } from "@/types/api";

/** GET /api/projets/ — projets de l'utilisateur connecté, enveloppe de pagination DRF retirée. */
export async function recupererProjets(): Promise<Projet[]> {
  const reponse = await api.get<Response<Projet>>("/projets/");
  return reponse.data.results;
}
