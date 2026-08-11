import type { Projet } from "@/types/api";
import { classeResistance } from "@/lib/beton";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type CarteProjetProps = {
  projet: Projet;
};

export function CarteProjet({ projet }: CarteProjetProps) {
  const dateFormatee = new Date(projet.date_creation).toLocaleDateString(
    "fr-FR",
    {
      day: "numeric",
      month: "long",
      year: "numeric",
    },
  );
  return (
    <Card>
      <CardHeader>
        <CardTitle>{projet.nom}</CardTitle>
        {projet.description && (
          <CardDescription>{projet.description}</CardDescription>
        )}{" "}
      </CardHeader>
      <CardContent className="flex gap-2">
        <Badge variant="secondary">{classeResistance(projet.fck)}</Badge>
        <Badge variant="secondary">{projet.classe_exposition}</Badge>
        <span className="text-xs text-muted-foreground ml-auto">
          Créé le {dateFormatee}
        </span>
      </CardContent>
    </Card>
  );
}
