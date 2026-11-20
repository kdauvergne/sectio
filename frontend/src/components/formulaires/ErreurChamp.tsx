import { TriangleAlert } from "lucide-react";
import { FieldError } from "@/components/ui/field";
import type { Erreurs } from "@/lib/formulaires";

export function ErreurChamp({ erreurs }: { erreurs: Erreurs }) {
  const message = erreurs.find((erreur) => erreur?.message)?.message;
  if (!message) return null;
  return (
    <FieldError className="flex items-start gap-1.5">
      <TriangleAlert className="mt-0.5 size-3.5 shrink-0" />
      <span>{message}</span>
    </FieldError>
  );
}
