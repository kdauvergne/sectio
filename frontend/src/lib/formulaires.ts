export type Erreurs = Array<{ message?: string } | undefined>;

export function compterErreurs(
  fieldMeta: Record<string, { errors?: Erreurs } | undefined>,
): number {
  return Object.values(fieldMeta).filter((meta) => meta?.errors?.length).length;
}

export function focaliserPremiereErreur(idFormulaire: string): void {
  document
    .querySelector<HTMLElement>(`#${idFormulaire} [aria-invalid="true"]`)
    ?.focus();
}

export function resumeHypotheses(hypotheses: {
  fck: number;
  fyk: number;
  classe_exposition: string;
}): string {
  return `fck ${hypotheses.fck} · fyk ${hypotheses.fyk} · ${hypotheses.classe_exposition || "—"}`;
}

export function suggestionsNiveaux(nomsExistants: string[]): string[] {
  const pris = new Set(nomsExistants.map((nom) => nom.trim().toLowerCase()));
  const libre = (nom: string) => !pris.has(nom.toLowerCase());
  const etages: string[] = [];
  for (let k = 1; etages.length < 3; k++) {
    if (libre(`N+${k}`)) etages.push(`N+${k}`);
  }
  return [...["Sous-sol", "RDC"].filter(libre), ...etages];
}
