import { Field, FieldDescription, FieldLabel } from "@/components/ui/field";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ErreurChamp } from "@/components/formulaires/ErreurChamp";
import {
  CODES_EXPOSITION,
  type ClasseExposition,
  LIBELLES_EXPOSITION,
} from "@/lib/beton";
import type { Erreurs } from "@/lib/formulaires";

type Props = {
  id: string;
  valeur: string;
  onChange: (valeur: ClasseExposition) => void;
  onBlur: () => void;
  erreurs: Erreurs;
  aide?: string;
};

export function SelectExposition({
  id,
  valeur,
  onChange,
  onBlur,
  erreurs,
  aide,
}: Props) {
  const estInvalide = erreurs.some((erreur) => erreur?.message);
  return (
    <Field data-invalid={estInvalide} className="sm:col-span-2">
      <FieldLabel htmlFor={id}>Classe d'exposition</FieldLabel>
      <Select
        value={valeur}
        onValueChange={(code) => onChange(code as ClasseExposition)}
      >
        <SelectTrigger
          id={id}
          className="w-full rounded-md data-[size=default]:h-9"
          onBlur={onBlur}
          aria-invalid={estInvalide}
        >
          <SelectValue placeholder="Choisissez une classe d'exposition" />
        </SelectTrigger>
        <SelectContent>
          {CODES_EXPOSITION.map((code) => (
            <SelectItem key={code} value={code}>
              <span className="font-mono">{code}</span>
              <span className="text-muted-foreground">
                {LIBELLES_EXPOSITION[code]}
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {aide && !estInvalide && <FieldDescription>{aide}</FieldDescription>}
      <ErreurChamp erreurs={erreurs} />
    </Field>
  );
}
