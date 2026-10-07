import { api } from "@/lib/api";
import type {
  NiveauDetail,
  Projet,
  ProjetDetail,
  Response,
} from "@/types/api";

/** GET /api/projets/ — projets de l'utilisateur connecté, enveloppe de pagination DRF retirée. */
export async function recupererProjets(): Promise<Projet[]> {
  const reponse = await api.get<Response<Projet>>("/projets/");
  return reponse.data.results;
}

/** GET /api/projets/{id}/ un projet de l'utilisateur connecté, avec ses bâtiments (sans leurs niveaux). */
export async function recupererProjet(id: string): Promise<ProjetDetail> {
  const reponse = await api.get<ProjetDetail>(`/projets/${id}/`);
  return reponse.data;
}

/** GET /api/niveaux/{id}/ — un niveau, avec les noms de son bâtiment et de son projet. */
export async function recupererNiveau(id: number): Promise<NiveauDetail> {
  const reponse = await api.get<NiveauDetail>(`/niveaux/${id}/`);
  return reponse.data;
}
