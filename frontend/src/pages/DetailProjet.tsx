import { useParams, Link } from "react-router-dom";

import { recupererProjet } from "@/api/projets";
import { FilAriane } from "@/components/layout/FilAriane";
import { Skeleton } from "@/components/ui/skeleton";
import { skipToken, useQuery } from "@tanstack/react-query";
import {
  Item,
  ItemMedia,
  ItemContent,
  ItemTitle,
  ItemDescription,
  ItemActions,
  ItemGroup,
} from "@/components/ui/item";
import { Building2, ChevronRight } from "lucide-react";

export function DetailProjet() {
  const { id } = useParams();
  const {
    data: projet,
    isPending,
    isError,
  } = useQuery({
    queryKey: ["projets", id],
    queryFn: id ? () => recupererProjet(id) : skipToken,
  });
  return (
    <div className="p-6">
      <FilAriane
        elements={[
          { libelle: "Projets", url: "/projets" },
          { libelle: projet?.nom ?? "…" },
        ]}
      />
      <h1 className="text-2xl font-semibold">{projet?.nom}</h1>

      {isPending && (
        <div className="mt-4 flex flex-col gap-3">
          <Skeleton className="h-5 w-64" />
          <Skeleton className="h-24 w-full rounded-xl" />
        </div>
      )}

      {isError && (
        <p className="mt-4 text-sm text-destructive">
          Impossible de charger le projet.
        </p>
      )}

      {!isPending && !isError && projet.description && (
        <p className="mt-2 max-w-2xl text-muted-foreground">
          {projet.description}
        </p>
      )}

      <h2 className="text-xl font-semibold mt-10 mb-4">Bâtiments</h2>

      {!isPending && !isError && projet.batiments.length === 0 && (
        <p className="text-muted-foreground text-sm">
          Aucun bâtiment pour ce projet.
        </p>
      )}
      <div className="flex flex-col gap-5">
        {!isPending &&
          !isError &&
          projet.batiments.map((batiment) => (
            <div
              key={batiment.id}
              className="overflow-hidden rounded-xl border"
            >
              {/* En-tête */}
              <Item className="gap-3 rounded-none border-b bg-muted px-4 py-3.5">
                <ItemMedia className="text-muted-foreground">
                  <Building2 className="size-4" />
                </ItemMedia>
                <ItemContent className="flex-row items-baseline gap-3">
                  <ItemTitle className="text-[15px] font-semibold">
                    {batiment.nom}
                  </ItemTitle>
                  <ItemDescription className="text-[12.5px]">
                    {batiment.niveaux.length} niveaux
                  </ItemDescription>
                </ItemContent>
                <ItemActions className="font-mono text-xs text-muted-foreground">
                  fck {batiment.fck} · fyk {batiment.fyk} ·{" "}
                  {batiment.classe_exposition}
                </ItemActions>
              </Item>

              {/* Niveaux */}
              <ItemGroup className="gap-0">
                {batiment.niveaux.map((niveau) => (
                  <Item
                    key={niveau.id}
                    asChild
                    className="rounded-none border-b py-3 pr-4 pl-12 last:border-b-0 hover:bg-accent"
                  >
                    <Link to={`/niveaux/${niveau.id}`}>
                      <ItemContent>
                        <ItemTitle className="text-[15px] font-medium">
                          {niveau.nom}
                        </ItemTitle>
                      </ItemContent>
                      <ItemActions className="text-muted-foreground">
                        <ChevronRight className="size-4" />
                      </ItemActions>
                    </Link>
                  </Item>
                ))}
              </ItemGroup>

              {batiment.niveaux.length === 0 && (
                <p className="px-4 py-3 pl-12 text-sm text-muted-foreground">
                  Aucun niveau.
                </p>
              )}
            </div>
          ))}
      </div>
    </div>
  );
}
