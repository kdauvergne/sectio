import type { Poteau } from "@/types/api";

/** Libellé lisible de la section, ex. "0,30 × 0,30 m" ou "Ø 0,50 m". */
export function libelleSection(poteau: Poteau): string {
  if (poteau.type_section === "circulaire") {
    if (poteau.diametre === null) return "—";
    return `Ø ${formaterMetres(poteau.diametre)} m`;
  }

  if (poteau.b === null || poteau.h === null) return "—";
  return `${formaterMetres(poteau.b)} × ${formaterMetres(poteau.h)} m`;
}

function formaterMetres(valeur: number): string {
  return valeur.toFixed(2).replace(".", ",");
}
