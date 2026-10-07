import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

type BarreRechercheProps = {
  valeur: string;
  onChangement: (nouvelleValeur: string) => void;
};

export function BarreRecherche({ valeur, onChangement }: BarreRechercheProps) {
  return (
    <div className="relative flex-1">
      <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        placeholder="Rechercher un projet"
        value={valeur}
        onChange={(e) => onChangement(e.target.value)}
        className="h-9 pl-9"
      />
    </div>
  );
}
