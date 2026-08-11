import { Input } from "@/components/ui/input";

type BarreRechercheProps = {
  valeur: string;
  onChangement: (nouvelleValeur: string) => void;
};

export function BarreRecherche({ valeur, onChangement }: BarreRechercheProps) {
  return (
    <div>
      <Input
        placeholder="Rechercher un projet..."
        value={valeur}
        onChange={(e) => onChangement(e.target.value)}
      />
    </div>
  );
}
