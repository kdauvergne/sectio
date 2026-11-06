import type { Projet } from "@/types/api";
import { PastilleProjet } from "@/components/projets/PastilleProjet";
import { dateRelative } from "@/lib/projets";
import { Link } from "react-router-dom";

type LigneProjetProps = {
  projet: Projet;
};

export function LigneProjet({ projet }: LigneProjetProps) {
  return (
    <Link
      to={`/projets/${projet.id}`}
      className="flex items-center gap-4 border-t px-2 py-4 transition hover:bg-muted"
    >
      <PastilleProjet nom={projet.nom} className="size-7 text-[12.5px]" />
      <span className="nom-ligne min-w-0 flex-1 truncate">{projet.nom}</span>
      <span className="info shrink-0 text-muted-foreground">
        {dateRelative(projet.date_creation)}
      </span>
    </Link>
  );
}
