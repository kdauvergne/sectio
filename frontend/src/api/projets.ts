import { api } from "@/lib/api";
import type {
  Batiment,
  Niveau,
  NiveauDetail,
  NouveauBatiment,
  NouveauNiveau,
  NouveauProjet,
  Projet,
  ProjetDetail,
  Response,
} from "@/types/api";

/** GET /api/projets/ — projets de l'utilisateur connecté, enveloppe de pagination DRF retirée. */
export async function recupererProjets(): Promise<Projet[]> {
  const reponse = await api.get<Response<Projet>>("/projets/");
  return reponse.data.results;
}

/** POST /api/projets/ — crée un projet ; l'utilisateur connecté en devient membre. */
export async function creerProjet(projet: NouveauProjet): Promise<Projet> {
  const reponse = await api.post<Projet>("/projets/", projet);
  return reponse.data;
}

/** GET /api/projets/{id}/ un projet de l'utilisateur connecté, avec ses bâtiments (sans leurs niveaux). */
export async function recupererProjet(id: string): Promise<ProjetDetail> {
  const reponse = await api.get<ProjetDetail>(`/projets/${id}/`);
  return reponse.data;
}

/** POST /api/batiments/ — crée un bâtiment dans un projet dont l'utilisateur est membre. */
export async function creerBatiment(
  batiment: NouveauBatiment,
): Promise<Batiment> {
  const reponse = await api.post<Batiment>("/batiments/", batiment);
  return reponse.data;
}

/** POST /api/niveaux/ — crée un niveau dans un bâtiment ; nom unique par bâtiment. */
export async function creerNiveau(niveau: NouveauNiveau): Promise<Niveau> {
  const reponse = await api.post<Niveau>("/niveaux/", niveau);
  return reponse.data;
}

/** GET /api/niveaux/{id}/ — un niveau, avec les noms de son bâtiment et de son projet. */
export async function recupererNiveau(id: number): Promise<NiveauDetail> {
  const reponse = await api.get<NiveauDetail>(`/niveaux/${id}/`);
  return reponse.data;
}
