import { useState } from "react";
import { useParams, Link } from "react-router-dom";

import { recupererProjet } from "@/api/projets";
import { Skeleton } from "@/components/ui/skeleton";
import { useFilAriane } from "@/hooks/use-fil-ariane";
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
import { Building2, ChevronRight, Plus } from "lucide-react";
import { DialogueNouveauBatiment } from "@/components/projets/DialogueNouveauBatiment";
import { DialogueNouveauNiveau } from "@/components/projets/DialogueNouveauNiveau";
import { Button } from "@/components/ui/button";

export function DetailProjet() {
  const { id } = useParams();
  const [nouveauBatimentOuvert, setNouveauBatimentOuvert] = useState(false);
  const [nouveauNiveauOuvert, setNouveauNiveauOuvert] = useState(false);
  // Gardé à la fermeture : le dialogue reste monté pendant son animation.
  const [batimentCibleId, setBatimentCibleId] = useState<number | null>(null);
  const {
    data: projet,
    isPending,
    isError,
  } = useQuery({
    queryKey: ["projets", id],
    queryFn: id ? () => recupererProjet(id) : skipToken,
  });

  const batimentCible = projet?.batiments.find(
    (batiment) => batiment.id === batimentCibleId,
  );

  function ouvrirNouveauNiveau(batimentId: number) {
    setBatimentCibleId(batimentId);
    setNouveauNiveauOuvert(true);
  }

  useFilAriane([
    { libelle: "Projets", url: "/" },
    { libelle: projet?.nom ?? "…" },
  ]);

  return (
    <div className="p-6">
      <h1 className="titre-projet">{projet?.nom}</h1>

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

      <div className="mt-10 mb-4 flex items-center justify-between gap-6">
        <h2 className="titre-section">Bâtiments</h2>
        {projet && (
          <Button size="sm" onClick={() => setNouveauBatimentOuvert(true)}>
            <Plus />
            Ajouter un bâtiment
          </Button>
        )}
      </div>

      {projet && (
        <DialogueNouveauBatiment
          projet={projet}
          ouvert={nouveauBatimentOuvert}
          onOuvertChange={setNouveauBatimentOuvert}
        />
      )}
      {projet && batimentCible && (
        <DialogueNouveauNiveau
          key={batimentCible.id}
          batiment={batimentCible}
          nomProjet={projet.nom}
          ouvert={nouveauNiveauOuvert}
          onOuvertChange={setNouveauNiveauOuvert}
        />
      )}

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
                    className="rounded-none border-b py-3 pr-4 pl-12 hover:bg-accent"
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

              <button
                type="button"
                onClick={() => ouvrirNouveauNiveau(batiment.id)}
                className="info flex w-full items-center gap-2 py-3 pr-4 pl-12 text-left text-muted-foreground outline-none hover:bg-accent hover:text-foreground focus-visible:bg-accent focus-visible:text-foreground"
              >
                <Plus className="size-3.5" />
                Ajouter un niveau à {batiment.nom}
              </button>
            </div>
          ))}
      </div>
    </div>
  );
}
