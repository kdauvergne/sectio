import { initiale } from "@/lib/projets";
import { cn } from "@/lib/utils";

type PastilleProjetProps = {
  nom: string;
  className?: string;
};

export function PastilleProjet({ nom, className }: PastilleProjetProps) {
  return (
    <span
      className={cn(
        "flex shrink-0 items-center justify-center rounded bg-primary/10 font-bold text-primary",
        className,
      )}
    >
      {initiale(nom)}
    </span>
  );
}
