import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { recupererNiveau } from "@/api/projets";
import { TableauPoteaux } from "@/components/poteaux/TableauPoteaux";
import { Skeleton } from "@/components/ui/skeleton";
import { useFilAriane } from "@/hooks/use-fil-ariane";
import type { NiveauDetail } from "@/types/api";

function titreNiveau({ nom, poteaux }: NiveauDetail): string {
  if (poteaux.length === 0) return `Niveau ${nom}`;
  const saisis = poteaux.length > 1 ? "poteaux saisis" : "poteau saisi";
  return `Niveau ${nom} — ${poteaux.length} ${saisis}`;
}

export function SaisieNiveau() {
  const { niveauId } = useParams();
  const identifiant = Number(niveauId);
  const identifiantValide = Number.isInteger(identifiant);

  const {
    data: niveau,
    isPending,
    isError,
  } = useQuery({
    queryKey: ["niveaux", identifiant],
    queryFn: () => recupererNiveau(identifiant),
    enabled: identifiantValide,
  });

  useFilAriane(
    niveau
      ? [
          { libelle: "Projets", url: "/" },
          { libelle: niveau.projet_nom, url: `/projets/${niveau.projet}` },
          { libelle: niveau.batiment_nom },
          { libelle: niveau.nom },
        ]
      : [{ libelle: "Projets", url: "/" }],
  );

  if (!identifiantValide) {
    return <p className="text-destructive p-8">Niveau introuvable.</p>;
  }

  if (isPending) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-7 w-80" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <p className="text-destructive p-6 text-sm">
        Impossible de charger le niveau.
      </p>
    );
  }

  const hypotheses = [
    { libelle: "fck", valeur: `${niveau.fck} MPa` },
    { libelle: "fyk", valeur: `${niveau.fyk} MPa` },
    { libelle: "Exposition", valeur: niveau.classe_exposition },
  ];
  const calcule = niveau.poteaux.some((poteau) => poteau.type_poteau !== null);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-end justify-between gap-6">
        <div className="flex flex-col gap-2.5">
          <h1 className="titre-niveau">{titreNiveau(niveau)}</h1>
          <div className="flex flex-wrap items-center gap-2">
            <span className="entete-tableau text-muted-foreground uppercase">
              Hypothèses du niveau
            </span>
            {hypotheses.map(({ libelle, valeur }) => (
              <span
                key={libelle}
                className="info-carte inline-flex items-baseline gap-1.5 rounded-md border px-2.25 py-0.75"
              >
                <span className="text-muted-foreground">{libelle}</span>
                <span className="font-mono">{valeur}</span>
              </span>
            ))}
          </div>
        </div>
        <span className="info-carte text-muted-foreground shrink-0">
          {calcule ? "Calculé" : "Jamais calculé"}
        </span>
      </div>

      <TableauPoteaux
        key={identifiant}
        niveauId={identifiant}
        poteaux={niveau.poteaux}
      />
    </div>
  );
}
