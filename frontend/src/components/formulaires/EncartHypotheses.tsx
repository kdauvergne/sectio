import type { ReactNode } from "react";
import { Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FieldSet } from "@/components/ui/field";

type Props = {
  source: string;
  cible: string;
  resume: string;
  deplie: boolean;
  onModifier: () => void;
  children: ReactNode;
};

export function EncartHypotheses({
  source,
  cible,
  resume,
  deplie,
  onModifier,
  children,
}: Props) {
  const rappel = (
    <p className="info-carte text-muted-foreground">
      Ces valeurs sont copiées maintenant : les modifier plus tard sur le{" "}
      {source} ne changera pas ce {cible}.
    </p>
  );

  if (!deplie) {
    return (
      <div className="flex flex-col gap-2.5">
        <div className="flex items-center gap-3.5 rounded-lg border bg-card p-3.5">
          <div className="flex min-w-0 flex-1 flex-col gap-1.5">
            <span className="info-carte text-muted-foreground">
              Hypothèses recopiées du {source}
            </span>
            <span className="info font-mono">{resume}</span>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onModifier}
          >
            <Pencil />
            Modifier
          </Button>
        </div>
        {rappel}
      </div>
    );
  }

  return (
    // La bordure est sur le conteneur : sur un fieldset, la légende la couperait.
    <div className="rounded-lg border bg-card p-4">
      <FieldSet className="gap-3">
        <legend className="entete-tableau mb-3 uppercase text-muted-foreground">
          Hypothèses du {cible}
        </legend>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">{children}</div>
        {rappel}
      </FieldSet>
    </div>
  );
}
