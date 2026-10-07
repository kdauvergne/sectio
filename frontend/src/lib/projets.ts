const MINUTE = 60_000;
const HEURE = 3_600_000;
const JOUR = 86_400_000;

/** Première lettre du nom, en majuscule, pour la pastille du projet */
export function initiale(nom: string): string {
  return nom.trim().charAt(0).toUpperCase();
}

/** Date relative en français */
export function dateRelative(iso: string, maintenant = Date.now()): string {
  const ecart = maintenant - new Date(iso).getTime();
  if (ecart < 45 * MINUTE) return "à l'instant";
  if (ecart < 2 * HEURE) return "il y a 1 h";
  if (ecart < JOUR) return `il y a ${Math.round(ecart / HEURE)} h`;
  if (ecart < 2 * JOUR) return "hier";
  if (ecart < 7 * JOUR) return `il y a ${Math.round(ecart / JOUR)} jours`;
  if (ecart < 30 * JOUR) {
    const semaines = Math.round(ecart / (7 * JOUR));
    return `il y a ${semaines} ${semaines > 1 ? "semaines" : "semaine"}`;
  }
  return `il y a ${Math.round(ecart / (30 * JOUR))} mois`;
}

/** Compteur de la section : "3 projets", ou "1 projet trouvé" pendant une recherche. */
export function compteurProjets(nombre: number, recherche: boolean): string {
  const pluriel = nombre > 1;
  if (recherche)
    return `${nombre} ${pluriel ? "projets trouvés" : "projet trouvé"}`;
  return `${nombre} ${pluriel ? "projets" : "projet"}`;
}
