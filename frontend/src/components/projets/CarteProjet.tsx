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
import { Square } from "lucide-react";

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
    <Card className="w-full max-w-xs min-h-40 my-5">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="w-fit rounded bg-primary/10 p-2">
            <Square className="size-4 text-primary" />
          </div>
          <div>
            <Badge variant="default">Conforme</Badge>
          </div>
        </div>
        <CardTitle className="pt-5">{projet.nom}</CardTitle>
        <CardDescription>{projet.description}</CardDescription>
      </CardHeader>
      <CardContent className="mt-auto">
        <div className="flex gap-2">
          <Badge variant="secondary">{classeResistance(projet.fck)}</Badge>

          <Badge variant="secondary">{projet.classe_exposition}</Badge>
        </div>

        <span className="mt-3 block text-xs text-muted-foreground">
          Créé le {dateFormatee}
        </span>
      </CardContent>
    </Card>
  );
}
