import type { AnyFieldApi } from "@tanstack/react-form";
import { Input } from "@/components/ui/input";

type Props = {
  field: AnyFieldApi;
  disabled?: boolean;
};

export function ChampNumerique({ field, disabled }: Props) {
  const estInvalide = field.state.meta.isTouched && !field.state.meta.isValid;

  return (
    <>
      <Input
        name={field.name}
        type="number"
        step="any"
        disabled={disabled}
        value={field.state.value ?? ""}
        onBlur={field.handleBlur}
        onChange={(e) =>
          field.handleChange(
            e.target.value === "" ? null : Number(e.target.value),
          )
        }
        aria-invalid={estInvalide}
        className="h-8 [appearance:textfield] px-2 text-right [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
      />
      {estInvalide && (
        <p className="text-destructive mt-1 text-xs">
          {field.state.meta.errors[0]?.message}
        </p>
      )}
    </>
  );
}
