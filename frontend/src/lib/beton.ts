/**
 * Classes de résistance du béton issues de l'EC2 Tableau 3.1.
 * Correspondance fck (cylindre) vers fck,cube, en MPa.
 */
const CLASSES_RESISTANCE: Record<number, number> = {
  12: 15,
  16: 20,
  20: 25,
  25: 30,
  30: 37,
  35: 45,
  40: 50,
  45: 55,
  50: 60,
  55: 67,
  60: 75,
  70: 85,
  80: 95,
  90: 105,
};

/** Libellé normalisé d'une classe de résistance, ex. "C30/37". */
export function classeResistance(fck: number): string {
  const cube = CLASSES_RESISTANCE[fck];
  return cube === undefined ? `C${fck}` : `C${fck}/${cube}`;
}

/**
 * Classes d'exposition proposées à la saisie, regroupées comme
 * tables_enrobage.json. Libellés d'après l'EC2 Tableau 4.1 et les notes 3 et 4
 * de l'Annexe nationale (NF EN 1992-1-1/NA).
 */
export const CODES_EXPOSITION = [
  "X0",
  "XC1",
  "XC2/XC3",
  "XC4",
  "XD1/XS1",
  "XD2/XS2",
  "XD3/XS3",
] as const;

export type ClasseExposition = (typeof CODES_EXPOSITION)[number];

export const LIBELLES_EXPOSITION: Record<ClasseExposition, string> = {
  X0: "Aucun risque de corrosion — béton armé en milieu très sec",
  XC1: "Sec ou humide en permanence — courant en bâtiment",
  "XC2/XC3": "Humide, rarement sec · humidité modérée",
  XC4: "Alternativement humide et sec — exposé à la pluie",
  "XD1/XS1": "Chlorures, humidité modérée · air marin",
  "XD2/XS2": "Chlorures, humide rarement sec · immergé en eau de mer",
  "XD3/XS3": "Chlorures, alternativement humide et sec · marnage, embruns",
};
