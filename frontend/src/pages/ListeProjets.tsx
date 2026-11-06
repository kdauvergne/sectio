import { CarteProjet } from "@/components/projets/CarteProjet";
import { LigneProjet } from "@/components/projets/LigneProjet";
import { useQuery } from "@tanstack/react-query";
import { LayoutGrid, List } from "lucide-react";
import { useState } from "react";
import { recupererProjets } from "@/api/projets";
import { BarreRecherche } from "@/components/projets/BarreRecherche";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/contexts/AuthContext";
import {
  type AffichageProjets,
  compteurProjets,
  enregistrerAffichage,
  lireAffichage,
} from "@/lib/projets";

function dateDuJour(): string {
  const date = new Date().toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  return date.charAt(0).toUpperCase() + date.slice(1);
}

export function ListeProjets() {
  const { utilisateur } = useAuth();
  const [recherche, setRecherche] = useState("");
  const [affichage, setAffichage] = useState(lireAffichage);

  function changerAffichage(nouvelAffichage: AffichageProjets) {
    setAffichage(nouvelAffichage);
    enregistrerAffichage(nouvelAffichage);
  }

  const {
    data: projets,
    isPending,
    isError,
  } = useQuery({
    queryKey: ["projets"],
    queryFn: recupererProjets,
  });

  const filtre = recherche.trim().toLowerCase();
  const projetFiltres = (projets ?? []).filter((projet) =>
    projet.nom.toLowerCase().includes(filtre),
  );

  return (
    <div className="w-full pt-8 pb-16">
      <div className="flex flex-col gap-1.5">
        <h1 className="text-[32px] leading-tight font-semibold tracking-tight">
          Bonjour {utilisateur?.first_name}
        </h1>
        <span className="text-sm text-muted-foreground">{dateDuJour()}</span>
      </div>

      <div className="mt-13 flex items-end justify-between gap-6 border-t pt-5">
        <div className="flex items-baseline gap-2.5">
          <h2 className="text-[15px] font-semibold">Tous les projets</h2>
          {projets && (
            <span className="text-[13px] text-muted-foreground">
              {compteurProjets(projetFiltres.length, filtre !== "")}
            </span>
          )}
        </div>
      </div>

      <div className="mt-4 mb-6 flex items-center gap-3">
        <BarreRecherche valeur={recherche} onChangement={setRecherche} />
        <div className="flex shrink-0 gap-0.5 rounded-lg border p-px">
          <Button
            variant={affichage === "liste" ? "secondary" : "ghost"}
            size="icon-sm"
            aria-label="Afficher en liste"
            aria-pressed={affichage === "liste"}
            onClick={() => changerAffichage("liste")}
          >
            <List />
          </Button>
          <Button
            variant={affichage === "cartes" ? "secondary" : "ghost"}
            size="icon-sm"
            aria-label="Afficher en cartes"
            aria-pressed={affichage === "cartes"}
            onClick={() => changerAffichage("cartes")}
          >
            <LayoutGrid />
          </Button>
        </div>
      </div>

      {isError && (
        <p className="text-sm text-destructive">
          Impossible de charger les projets.
        </p>
      )}

      {affichage === "cartes" ? (
        <div className="grid auto-rows-fr grid-cols-3 gap-4 xl:grid-cols-5">
          {isPending &&
            Array.from({ length: 3 }, (_, index) => (
              <Skeleton key={index} className="h-40 w-full rounded-xl" />
            ))}

          {!isPending &&
            !isError &&
            projetFiltres.map((projet) => (
              <CarteProjet key={projet.id} projet={projet} />
            ))}
        </div>
      ) : (
        <div className="flex flex-col">
          {isPending &&
            Array.from({ length: 3 }, (_, index) => (
              <Skeleton key={index} className="my-2 h-11 w-full rounded-lg" />
            ))}

          {!isPending &&
            !isError &&
            projetFiltres.map((projet) => (
              <LigneProjet key={projet.id} projet={projet} />
            ))}
        </div>
      )}

      {!isPending && !isError && filtre !== "" && projetFiltres.length === 0 && (
        <div className="flex flex-col items-start gap-3.5 border-t py-11">
          <p className="text-sm text-muted-foreground">
            Aucun projet ne correspond à « {recherche.trim()} ».
          </p>
          <Button variant="outline" size="sm" onClick={() => setRecherche("")}>
            Effacer le filtre
          </Button>
        </div>
      )}
    </div>
  );
}
