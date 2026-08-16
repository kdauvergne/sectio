import { api } from "@/lib/api";
import type { NouveauPoteau, Poteau, Response } from "@/types/api";

/** GET /api/poteaux/?niveau=… — poteaux déjà enregistrés sur un niveau */
export async function recupererPoteaux(niveauId: number): Promise<Poteau[]> {
  const reponse = await api.get<Response<Poteau>>("/poteaux/", {
    params: { niveau: niveauId },
  });
  return reponse.data.results;
}

/** POST /api/poteaux/  création en lot*/
export async function creerPoteaux(
  poteaux: NouveauPoteau[],
): Promise<Poteau[]> {
  const reponse = await api.post<Poteau[]>("/poteaux/", poteaux);
  return reponse.data;
}
