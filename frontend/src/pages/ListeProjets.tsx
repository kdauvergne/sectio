import { CarteProjet } from "@/components/projets/CarteProjet";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { recupererProjets } from "@/api/projets";
import { BarreRecherche } from "@/components/projets/BarreRecherche";
import { Skeleton } from "@/components/ui/skeleton";

export function ListeProjets() {
  const [recherche, setRecherche] = useState("");

  const {
    data: projets,
    isPending,
    isError,
  } = useQuery({
    queryKey: ["projets"],
    queryFn: recupererProjets,
  });

  const projetFiltres = (projets ?? []).filter((projet) =>
    projet.nom.toLowerCase().includes(recherche.toLowerCase()),
  );

  return (
    <div>
      <div className="grid gap-4 max-w-2xl mx-5 ">
        <h1 className="text-2xl font-semibold mb-6">Projets</h1>
      </div>
      <div className="mb-6">
        <BarreRecherche valeur={recherche} onChangement={setRecherche} />
      </div>
      <div className="grid grid-cols-3 gap-4 xl:grid-cols-5">
        {isPending &&
          Array.from({ length: 3 }, (_, index) => (
            <Skeleton
              key={index}
              className="my-5 h-40 w-full max-w-xs rounded-xl"
            />
          ))}

        {isError && (
          <p className="text-sm text-destructive">
            Impossible de charger les projets.
          </p>
        )}

        {!isPending &&
          !isError &&
          projetFiltres.map((projet) => (
            <CarteProjet key={projet.id} projet={projet} />
          ))}

        {!isPending && !isError && projetFiltres.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Aucun projet ne correspond à « {recherche} ».
          </p>
        )}
      </div>
    </div>
  );
}
