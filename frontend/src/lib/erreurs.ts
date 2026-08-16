import { isAxiosError } from "axios";

function collecterMessages(valeur: unknown): string[] {
  if (typeof valeur === "string") return [valeur];
  if (Array.isArray(valeur)) return valeur.flatMap(collecterMessages);
  if (valeur && typeof valeur === "object") {
    return Object.values(valeur).flatMap(collecterMessages);
  }
  return [];
}

export function messageErreurApi(erreur: unknown): string {
  if (!isAxiosError(erreur)) return "Erreur inattendue.";
  const messages = collecterMessages(erreur.response?.data);
  return messages.length > 0
    ? messages.join(" ")
    : "Enregistrement impossible.";
}
