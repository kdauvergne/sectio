import { Field, FieldDescription, FieldLabel } from "@/components/ui/field";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { ErreurChamp } from "@/components/formulaires/ErreurChamp";
import type { Erreurs } from "@/lib/formulaires";

type Props = {
  id: string;
  libelle: string;
  valeur: number;
  onChange: (valeur: number) => void;
  onBlur: () => void;
  erreurs: Erreurs;
  aide?: string;
  autoFocus?: boolean;
};

export function ChampMPa({
  id,
  libelle,
  valeur,
  onChange,
  onBlur,
  erreurs,
  aide,
  autoFocus,
}: Props) {
  const estInvalide = erreurs.some((erreur) => erreur?.message);
  return (
    <Field data-invalid={estInvalide}>
      <FieldLabel htmlFor={id}>{libelle}</FieldLabel>
      <InputGroup className="h-9 rounded-md">
        <InputGroupInput
          id={id}
          name={id}
          type="number"
          inputMode="decimal"
          className="font-mono"
          autoFocus={autoFocus}
          value={Number.isNaN(valeur) ? "" : valeur}
          onBlur={onBlur}
          onChange={(e) => onChange(e.target.valueAsNumber)}
          aria-invalid={estInvalide}
        />
        <InputGroupAddon align="inline-end">MPa</InputGroupAddon>
      </InputGroup>
      {aide && !estInvalide && <FieldDescription>{aide}</FieldDescription>}
      <ErreurChamp erreurs={erreurs} />
    </Field>
  );
}
