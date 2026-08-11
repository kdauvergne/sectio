import type { Projet } from "@/types/api";

export const PROJETS_DEMO: Projet[] = [
  {
    id: 1,
    nom: "Airbus Aerospace",
    description: "Montigny",
    date_creation: "2026-03-12T09:15:00Z",
    membres: [1],
    fck: 45,
    fyk: 500,
    classe_exposition: "XC1",
  },
  {
    id: 2,
    nom: "GA Smart Building",
    description: "",
    date_creation: "2026-05-02T14:40:00Z",
    membres: [1, 2],
    fck: 30,
    fyk: 500,
    classe_exposition: "XC3",
  },
];
