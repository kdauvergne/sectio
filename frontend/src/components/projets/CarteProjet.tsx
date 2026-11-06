import type { Projet } from "@/types/api";
import { PastilleProjet } from "@/components/projets/PastilleProjet";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { dateRelative } from "@/lib/projets";
import { Link } from "react-router-dom";

type CarteProjetProps = {
  projet: Projet;
};

export function CarteProjet({ projet }: CarteProjetProps) {
  return (
    <Link to={`/projets/${projet.id}`}>
      <Card className="h-full min-h-40 transition hover:shadow-md hover:-translate-y-1">
        <CardHeader>
          <PastilleProjet nom={projet.nom} className="size-7.5 text-[13px]" />
          <CardTitle className="line-clamp-2 pt-3">{projet.nom}</CardTitle>
        </CardHeader>
        <CardContent className="mt-auto text-xs text-muted-foreground">
          {dateRelative(projet.date_creation)}
        </CardContent>
      </Card>
    </Link>
  );
}
