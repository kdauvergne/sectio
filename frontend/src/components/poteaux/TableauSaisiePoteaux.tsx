import { useForm } from "@tanstack/react-form";
import { Plus, Trash2 } from "lucide-react";
import { schemaSaisieNiveau, type SaisiePoteau } from "@/schemas/poteau";
import { ChampNumerique } from "./ChampNumerique";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { creerPoteaux } from "@/api/poteaux";
import { messageErreurApi } from "@/lib/erreurs";
import { Alert, AlertDescription } from "@/components/ui/alert";

const LIGNE_VIDE = {
  repere: "",
  type_section: "rectangulaire",
  b: null,
  h: null,
  diametre: null,
  L0: null,
  d_prime: null,
  G: null,
  Q: null,
} as unknown as SaisiePoteau;

type Props = {
  niveauId: number;
};

export function TableauSaisiePoteaux({ niveauId }: Props) {
  const queryClient = useQueryClient();
  const [erreurServeur, setErreurServeur] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: creerPoteaux,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["poteaux", niveauId] }),
  });

  const form = useForm({
    defaultValues: { poteaux: [{ ...LIGNE_VIDE }] },
    validators: { onSubmit: schemaSaisieNiveau },
    onSubmit: async ({ value }) => {
      setErreurServeur(null);
      try {
        await mutation.mutateAsync(
          value.poteaux.map((poteau) => ({ ...poteau, niveau: niveauId })),
        );
        form.reset();
      } catch (erreur) {
        setErreurServeur(messageErreurApi(erreur));
      }
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <form.Field
        name="poteaux"
        mode="array"
        children={(champTableau) => (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Repère</TableHead>
                <TableHead>Section</TableHead>
                <TableHead>b (m)</TableHead>
                <TableHead>h (m)</TableHead>
                <TableHead>D (m)</TableHead>
                <TableHead>L0 (m)</TableHead>
                <TableHead>d' (m)</TableHead>
                <TableHead>G (kN)</TableHead>
                <TableHead>Q (kN)</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>

            <TableBody>
              {champTableau.state.value.map((_, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <form.Field
                      name={`poteaux[${index}].repere`}
                      children={(field) => (
                        <Input
                          name={field.name}
                          maxLength={8}
                          value={field.state.value}
                          onBlur={field.handleBlur}
                          onChange={(e) => field.handleChange(e.target.value)}
                          aria-invalid={
                            field.state.meta.isTouched &&
                            !field.state.meta.isValid
                          }
                          className="h-8 w-20"
                        />
                      )}
                    />
                  </TableCell>

                  <TableCell>
                    <form.Field name={`poteaux[${index}].type_section`}>
                      {(field) => (
                        <Select
                          value={field.state.value}
                          onValueChange={(valeur) => {
                            field.handleChange(
                              valeur as "rectangulaire" | "circulaire",
                            );
                            form.setFieldValue(`poteaux[${index}].b`, null);
                            form.setFieldValue(`poteaux[${index}].h`, null);
                            form.setFieldValue(
                              `poteaux[${index}].diametre`,
                              null,
                            );
                          }}
                        >
                          <SelectTrigger className="h-8 w-36">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="rectangulaire">
                              Rectangulaire
                            </SelectItem>
                            <SelectItem value="circulaire">
                              Circulaire
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    </form.Field>
                  </TableCell>

                  <form.Subscribe
                    selector={(etat) =>
                      etat.values.poteaux[index]?.type_section
                    }
                  >
                    {(typeSection) => (
                      <>
                        <TableCell>
                          <form.Field name={`poteaux[${index}].b`}>
                            {(field) => (
                              <ChampNumerique
                                field={field}
                                disabled={typeSection !== "rectangulaire"}
                              />
                            )}
                          </form.Field>
                        </TableCell>

                        <TableCell>
                          <form.Field name={`poteaux[${index}].h`}>
                            {(field) => (
                              <ChampNumerique
                                field={field}
                                disabled={typeSection !== "rectangulaire"}
                              />
                            )}
                          </form.Field>
                        </TableCell>

                        <TableCell>
                          <form.Field name={`poteaux[${index}].diametre`}>
                            {(field) => (
                              <ChampNumerique
                                field={field}
                                disabled={typeSection !== "circulaire"}
                              />
                            )}
                          </form.Field>
                        </TableCell>
                      </>
                    )}
                  </form.Subscribe>

                  <TableCell>
                    <form.Field name={`poteaux[${index}].L0`}>
                      {(field) => <ChampNumerique field={field} />}
                    </form.Field>
                  </TableCell>

                  <TableCell>
                    <form.Field name={`poteaux[${index}].d_prime`}>
                      {(field) => <ChampNumerique field={field} />}
                    </form.Field>
                  </TableCell>

                  <TableCell>
                    <form.Field name={`poteaux[${index}].G`}>
                      {(field) => <ChampNumerique field={field} />}
                    </form.Field>
                  </TableCell>

                  <TableCell>
                    <form.Field name={`poteaux[${index}].Q`}>
                      {(field) => <ChampNumerique field={field} />}
                    </form.Field>
                  </TableCell>

                  <TableCell>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="size-8"
                      onClick={() => champTableau.removeValue(index)}
                      disabled={champTableau.state.value.length === 1}
                      aria-label={`Supprimer la ligne ${index + 1}`}
                    >
                      <Trash2 />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>

            <TableFooter className="bg-transparent">
              <TableRow className="hover:bg-transparent">
                <TableCell colSpan={10} className="p-1">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="text-muted-foreground w-full justify-start font-normal"
                    onClick={() => champTableau.pushValue({ ...LIGNE_VIDE })}
                  >
                    <Plus /> Ajouter un poteau
                  </Button>
                </TableCell>
              </TableRow>
            </TableFooter>
          </Table>
        )}
      />

      <form.Subscribe selector={(etat) => etat.isValid}>
        {(estValide) =>
          estValide ? null : (
            <p className="text-destructive mt-4 text-sm">
              Certaines cellules sont incorrectes. Corrigez celles encadrées en
              rouge.
            </p>
          )
        }
      </form.Subscribe>

      {erreurServeur && (
        <Alert variant="destructive" className="mt-4">
          <AlertDescription>{erreurServeur}</AlertDescription>
        </Alert>
      )}

      <Button type="submit" className="mt-4" disabled={mutation.isPending}>
        {mutation.isPending ? "Enregistrement…" : "Enregistrer le niveau"}
      </Button>
    </form>
  );
}
