import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { recupererPoteaux } from "@/api/poteaux";
import { recupererNiveau } from "@/api/projets";
import { TableauPoteaux } from "@/components/poteaux/TableauPoteaux";
import { TableauSaisiePoteaux } from "@/components/poteaux/TableauSaisiePoteaux";
import { Skeleton } from "@/components/ui/skeleton";
import { useFilAriane } from "@/hooks/use-fil-ariane";

export function SaisieNiveau() {
  const { niveauId } = useParams();
  const identifiant = Number(niveauId);
  const identifiantValide = Number.isInteger(identifiant);

  const {
    data: poteaux,
    isPending,
    isError,
  } = useQuery({
    queryKey: ["poteaux", identifiant],
    queryFn: () => recupererPoteaux(identifiant),
    enabled: identifiantValide,
  });

  const { data: niveau } = useQuery({
    queryKey: ["niveaux", identifiant],
    queryFn: () => recupererNiveau(identifiant),
    enabled: identifiantValide,
  });

  useFilAriane(
    niveau
      ? [
          { libelle: "Projets", url: "/projets" },
          { libelle: niveau.projet_nom, url: `/projets/${niveau.projet}` },
          { libelle: niveau.batiment_nom },
          { libelle: niveau.nom },
        ]
      : [{ libelle: "Projets", url: "/projets" }],
  );

  if (!identifiantValide) {
    return <p className="text-destructive p-8">Niveau introuvable.</p>;
  }

  return (
    <div className="space-y-10 p-6">
      <h1 className="text-2xl font-semibold">{niveau?.nom}</h1>

      <section>
        <h2 className="mb-4 text-lg font-semibold">Poteaux enregistrés</h2>
        {isPending && <Skeleton className="h-32 w-full" />}
        {isError && (
          <p className="text-destructive text-sm">
            Impossible de charger les poteaux.
          </p>
        )}
        {poteaux && poteaux.length > 0 && <TableauPoteaux poteaux={poteaux} />}
        {poteaux && poteaux.length === 0 && (
          <p className="text-muted-foreground text-sm">
            Aucun poteau saisi pour l'instant.
          </p>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold">Ajouter des poteaux</h2>
        <TableauSaisiePoteaux niveauId={identifiant} />
      </section>
    </div>
  );
}
