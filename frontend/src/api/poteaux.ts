import { api } from "@/lib/api";
import type { SaisiePoteau } from "@/schemas/poteau";
import type { NouveauPoteau, Poteau } from "@/types/api";

const CHAMPS_MODIFIABLES = [
  "repere",
  "type_section",
  "b",
  "h",
  "diametre",
  "L0",
  "d_prime",
  "G",
  "Q",
] as const;

/** POST /api/poteaux/  création en lot*/
export async function creerPoteaux(
  poteaux: NouveauPoteau[],
): Promise<Poteau[]> {
  const reponse = await api.post<Poteau[]>("/poteaux/", poteaux);
  return reponse.data;
}

/** PATCH /api/poteaux/{id}/ */
export async function modifierPoteau(
  id: number,
  champs: Partial<NouveauPoteau>,
): Promise<Poteau> {
  const reponse = await api.patch<Poteau>(`/poteaux/${id}/`, champs);
  return reponse.data;
}

/** DELETE /api/poteaux/{id}/ */
export async function supprimerPoteau(id: number): Promise<void> {
  await api.delete(`/poteaux/${id}/`);
}

function estModifie(ligne: SaisiePoteau, poteau: Poteau): boolean {
  return CHAMPS_MODIFIABLES.some((champ) => ligne[champ] !== poteau[champ]);
}

/**
 * Applique les écarts entre le tableau et les poteaux enregistrés.
 * Les suppressions passent d'abord pour libérer leurs repères.
 * Non atomique : seule la création en lot, envoyée en dernier, l'est.
 */
export async function enregistrerPoteaux(
  niveauId: number,
  enregistres: Poteau[],
  lignes: SaisiePoteau[],
): Promise<void> {
  const conserves = new Set(lignes.map((ligne) => ligne.id));
  const supprimes = enregistres.filter(({ id }) => !conserves.has(id));
  await Promise.all(supprimes.map(({ id }) => supprimerPoteau(id)));

  const parId = new Map(enregistres.map((poteau) => [poteau.id, poteau]));
  for (const { id, ...champs } of lignes) {
    const poteau = id === undefined ? undefined : parId.get(id);
    if (id !== undefined && poteau && estModifie({ id, ...champs }, poteau)) {
      await modifierPoteau(id, champs);
    }
  }

  const nouveaux = lignes.filter(({ id }) => id === undefined);
  if (nouveaux.length > 0) {
    await creerPoteaux(
      nouveaux.map(({ id: _id, ...champs }) => ({
        ...champs,
        niveau: niveauId,
      })),
    );
  }
}
