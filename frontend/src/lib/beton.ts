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
