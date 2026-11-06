import { useForm } from "@tanstack/react-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Copy, MoreHorizontal, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { enregistrerPoteaux } from "@/api/poteaux";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { messageErreurApi } from "@/lib/erreurs";
import { schemaSaisieNiveau, type SaisiePoteau } from "@/schemas/poteau";
import type { NiveauDetail, Poteau } from "@/types/api";
import { ChampNumerique } from "./ChampNumerique";

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

const COLONNES = [
  { libelle: "Repère", largeur: "w-18" },
  { libelle: "Section", largeur: "w-36" },
  { libelle: "b (m)", largeur: "w-20", droite: true },
  { libelle: "h (m)", largeur: "w-20", droite: true },
  { libelle: "D (m)", largeur: "w-20", droite: true },
  { libelle: "L₀ (m)", largeur: "w-20", droite: true },
  { libelle: "d' (m)", largeur: "w-20", droite: true },
  { libelle: "G (kN)", largeur: "w-22", droite: true },
  { libelle: "Q (kN)", largeur: "w-22", droite: true },
  { libelle: "NEd (kN)", largeur: "w-22", droite: true },
  { libelle: "Type", largeur: "w-20" },
  { libelle: "", largeur: "w-11" },
];

function versLignes(poteaux: Poteau[]): SaisiePoteau[] {
  if (poteaux.length === 0) return [{ ...LIGNE_VIDE }];
  return poteaux.map(
    ({ id, repere, type_section, b, h, diametre, L0, d_prime, G, Q }) => ({
      id,
      repere,
      type_section,
      b,
      h,
      diametre,
      L0,
      d_prime,
      G,
      Q,
    }),
  );
}

type Props = {
  niveauId: number;
  poteaux: Poteau[];
};

export function TableauPoteaux({ niveauId, poteaux }: Props) {
  const queryClient = useQueryClient();
  const [erreurServeur, setErreurServeur] = useState<string | null>(null);
  const cleNiveau = ["niveaux", niveauId];

  const mutation = useMutation({
    mutationFn: (lignes: SaisiePoteau[]) =>
      enregistrerPoteaux(niveauId, poteaux, lignes),
    // Aussi en cas d'échec : une partie des requêtes a pu aboutir.
    onSettled: () => queryClient.invalidateQueries({ queryKey: cleNiveau }),
  });

  const form = useForm({
    defaultValues: { poteaux: versLignes(poteaux) },
    validators: { onSubmit: schemaSaisieNiveau },
    onSubmit: async ({ value }) => {
      setErreurServeur(null);
      try {
        await mutation.mutateAsync(value.poteaux);
        const niveau = queryClient.getQueryData<NiveauDetail>(cleNiveau);
        form.reset({ poteaux: versLignes(niveau?.poteaux ?? []) });
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
          <>
            <Table className="min-w-251">
              <TableHeader>
                <TableRow className="bg-muted hover:bg-muted">
                  {COLONNES.map(({ libelle, largeur, droite }) => (
                    <TableHead
                      key={libelle}
                      className={`entete-tableau font-semibold text-muted-foreground ${largeur} ${droite ? "text-right" : ""}`}
                    >
                      {libelle}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>

              <TableBody>
                {champTableau.state.value.map((ligne, index) => (
                  <TableRow key={index}>
                    <TableCell className="px-2 py-1">
                      <form.Field
                        name={`poteaux[${index}].repere`}
                        children={(field) => {
                          const estInvalide =
                            field.state.meta.isTouched &&
                            !field.state.meta.isValid;
                          return (
                            <>
                              <Input
                                name={field.name}
                                maxLength={8}
                                value={field.state.value}
                                onBlur={field.handleBlur}
                                onChange={(e) =>
                                  field.handleChange(e.target.value)
                                }
                                aria-invalid={estInvalide}
                                className="h-8 px-1.5 font-medium"
                              />
                              {estInvalide && (
                                <p className="text-destructive mt-1 text-xs">
                                  {field.state.meta.errors[0]?.message}
                                </p>
                              )}
                            </>
                          );
                        }}
                      />
                    </TableCell>

                    <TableCell className="px-2 py-1">
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
                            <SelectTrigger className="h-8 w-full">
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
                          <TableCell className="px-2 py-1">
                            <form.Field name={`poteaux[${index}].b`}>
                              {(field) => (
                                <ChampNumerique
                                  field={field}
                                  disabled={typeSection !== "rectangulaire"}
                                />
                              )}
                            </form.Field>
                          </TableCell>

                          <TableCell className="px-2 py-1">
                            <form.Field name={`poteaux[${index}].h`}>
                              {(field) => (
                                <ChampNumerique
                                  field={field}
                                  disabled={typeSection !== "rectangulaire"}
                                />
                              )}
                            </form.Field>
                          </TableCell>

                          <TableCell className="px-2 py-1">
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

                    <TableCell className="px-2 py-1">
                      <form.Field name={`poteaux[${index}].L0`}>
                        {(field) => <ChampNumerique field={field} />}
                      </form.Field>
                    </TableCell>

                    <TableCell className="px-2 py-1">
                      <form.Field name={`poteaux[${index}].d_prime`}>
                        {(field) => <ChampNumerique field={field} />}
                      </form.Field>
                    </TableCell>

                    <TableCell className="px-2 py-1">
                      <form.Field name={`poteaux[${index}].G`}>
                        {(field) => <ChampNumerique field={field} />}
                      </form.Field>
                    </TableCell>

                    <TableCell className="px-2 py-1">
                      <form.Field name={`poteaux[${index}].Q`}>
                        {(field) => <ChampNumerique field={field} />}
                      </form.Field>
                    </TableCell>

                    <TableCell className="text-muted-foreground px-2 py-1 text-right">
                      —
                    </TableCell>

                    <TableCell className="text-muted-foreground px-2 py-1">
                      —
                    </TableCell>

                    <TableCell className="px-2 py-1">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon-sm"
                            aria-label={`Actions de la ligne ${index + 1}`}
                          >
                            <MoreHorizontal />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onSelect={() =>
                              champTableau.insertValue(index + 1, {
                                ...ligne,
                                id: undefined,
                                repere: "",
                              })
                            }
                          >
                            <Copy /> Dupliquer la ligne
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            variant="destructive"
                            onSelect={() => champTableau.removeValue(index)}
                          >
                            <Trash2 /> Supprimer la ligne
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="text-muted-foreground mt-1 w-full"
              onClick={() => champTableau.pushValue({ ...LIGNE_VIDE })}
            >
              <Plus /> Ajouter un poteau
            </Button>
          </>
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
