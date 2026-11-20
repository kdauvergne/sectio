import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { revalidateLogic, useForm } from "@tanstack/react-form";
import { TriangleAlert } from "lucide-react";
import { creerProjet } from "@/api/projets";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldSet,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  CODES_EXPOSITION,
  type ClasseExposition,
  LIBELLES_EXPOSITION,
} from "@/lib/beton";
import { schemaNouveauProjet } from "@/schemas/projet";

const ID_FORMULAIRE = "form-nouveau-projet";

/** fck = 45 MPa et fyk = 500 MPa : défauts du modèle Projet. */
const VALEURS_INITIALES = {
  nom: "",
  fck: 45,
  fyk: 500,
  classe_exposition: "" as ClasseExposition | "",
};

type Erreurs = Array<{ message?: string } | undefined>;

/** Message d'erreur sous un champ, précédé de l'icône de la maquette. */
function ErreurChamp({ erreurs }: { erreurs: Erreurs }) {
  const message = erreurs.find((erreur) => erreur?.message)?.message;
  if (!message) return null;
  return (
    <FieldError className="flex items-start gap-1.5">
      <TriangleAlert className="mt-0.5 size-3.5 shrink-0" />
      <span>{message}</span>
    </FieldError>
  );
}

function compterErreurs(
  fieldMeta: Record<string, { errors?: Erreurs } | undefined>,
) {
  return Object.values(fieldMeta).filter((meta) => meta?.errors?.length).length;
}

type Props = {
  ouvert: boolean;
  onOuvertChange: (ouvert: boolean) => void;
};

export function DialogueNouveauProjet({ ouvert, onOuvertChange }: Props) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [confirmerQuitter, setConfirmerQuitter] = useState(false);

  const creation = useMutation({
    mutationFn: creerProjet,
    onSuccess: (projet) => {
      queryClient.invalidateQueries({ queryKey: ["projets"] });
      fermer();
      navigate(`/projets/${projet.id}`);
    },
  });

  const formProjet = useForm({
    defaultValues: VALEURS_INITIALES,
    // Validation à l'envoi, puis à chaque frappe après la première tentative.
    validationLogic: revalidateLogic(),
    validators: { onDynamic: schemaNouveauProjet },
    onSubmit: async ({ value }) => {
      await creation.mutateAsync(schemaNouveauProjet.parse(value));
    },
    onSubmitInvalid: () => {
      document
        .querySelector<HTMLElement>(`#${ID_FORMULAIRE} [aria-invalid="true"]`)
        ?.focus();
    },
  });

  function fermer() {
    formProjet.reset();
    creation.reset();
    setConfirmerQuitter(false);
    onOuvertChange(false);
  }

  /** Échap, Annuler ou clic hors du dialogue : confirmation seulement si la saisie a changé. */
  function demanderFermeture() {
    if (formProjet.state.isDirty) setConfirmerQuitter(true);
    else fermer();
  }

  return (
    <>
      <Dialog
        open={ouvert}
        onOpenChange={(estOuvert) =>
          estOuvert ? onOuvertChange(true) : demanderFermeture()
        }
      >
        <DialogContent
          showCloseButton={false}
          className="gap-5 p-6 sm:max-w-130"
        >
          <DialogHeader>
            <DialogTitle className="titre-dialogue font-semibold">
              Nouveau projet
            </DialogTitle>
            <DialogDescription className="sr-only">
              Nom du projet et hypothèses de calcul recopiées sur ses bâtiments
              et niveaux.
            </DialogDescription>
          </DialogHeader>

          <form
            id={ID_FORMULAIRE}
            noValidate
            onSubmit={(e) => {
              e.preventDefault();
              formProjet.handleSubmit();
            }}
          >
            <FieldGroup className="gap-5">
              <formProjet.Field
                name="nom"
                children={(field) => {
                  const estInvalide = !field.state.meta.isValid;
                  return (
                    <Field data-invalid={estInvalide}>
                      <FieldLabel htmlFor={field.name}>
                        Nom du projet
                      </FieldLabel>
                      <Input
                        id={field.name}
                        name={field.name}
                        autoFocus
                        autoComplete="off"
                        value={field.state.value}
                        onBlur={field.handleBlur}
                        onChange={(e) => field.handleChange(e.target.value)}
                        aria-invalid={estInvalide}
                      />
                      <ErreurChamp erreurs={field.state.meta.errors} />
                    </Field>
                  );
                }}
              />

              <div className="border-t pt-4">
                <FieldSet className="gap-3">
                  <legend className="entete-tableau mb-3 uppercase text-muted-foreground">
                    Hypothèses de calcul
                  </legend>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {(["fck", "fyk"] as const).map((nom) => (
                      <formProjet.Field
                        key={nom}
                        name={nom}
                        children={(field) => {
                          const estInvalide = !field.state.meta.isValid;
                          return (
                            <Field data-invalid={estInvalide}>
                              <FieldLabel htmlFor={field.name}>
                                {nom === "fck" ? "fck — béton" : "fyk — acier"}
                              </FieldLabel>
                              <InputGroup className="h-9 rounded-md">
                                <InputGroupInput
                                  id={field.name}
                                  name={field.name}
                                  type="number"
                                  inputMode="decimal"
                                  className="font-mono"
                                  value={
                                    Number.isNaN(field.state.value)
                                      ? ""
                                      : field.state.value
                                  }
                                  onBlur={field.handleBlur}
                                  onChange={(e) =>
                                    field.handleChange(e.target.valueAsNumber)
                                  }
                                  aria-invalid={estInvalide}
                                />
                                <InputGroupAddon align="inline-end">
                                  MPa
                                </InputGroupAddon>
                              </InputGroup>
                              <ErreurChamp erreurs={field.state.meta.errors} />
                            </Field>
                          );
                        }}
                      />
                    ))}

                    <formProjet.Field
                      name="classe_exposition"
                      children={(field) => {
                        const estInvalide = !field.state.meta.isValid;
                        return (
                          <Field
                            data-invalid={estInvalide}
                            className="sm:col-span-2"
                          >
                            <FieldLabel htmlFor={field.name}>
                              Classe d'exposition
                            </FieldLabel>
                            <Select
                              value={field.state.value}
                              onValueChange={(valeur) =>
                                field.handleChange(valeur as ClasseExposition)
                              }
                            >
                              <SelectTrigger
                                id={field.name}
                                className="w-full rounded-md data-[size=default]:h-9"
                                onBlur={field.handleBlur}
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
                            <ErreurChamp erreurs={field.state.meta.errors} />
                          </Field>
                        );
                      }}
                    />
                  </div>
                </FieldSet>
              </div>
            </FieldGroup>
          </form>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
            <formProjet.Subscribe
              selector={(etat) => compterErreurs(etat.fieldMeta)}
              children={(nbErreurs) => {
                if (creation.isError) {
                  return (
                    <p className="info-carte text-destructive">
                      Impossible de créer le projet. Réessayez.
                    </p>
                  );
                }
                if (nbErreurs > 0) {
                  return (
                    <p className="info-carte text-destructive">
                      {nbErreurs} {nbErreurs > 1 ? "champs" : "champ"} à
                      corriger
                    </p>
                  );
                }
                return (
                  <p className="hidden info-carte text-muted-foreground sm:block">
                    Entrée pour créer · Échap pour annuler
                  </p>
                );
              }}
            />
            <div className="flex flex-col-reverse gap-2 sm:flex-row">
              <Button
                type="button"
                variant="outline"
                onClick={demanderFermeture}
              >
                Annuler
              </Button>
              <Button
                type="submit"
                form={ID_FORMULAIRE}
                disabled={creation.isPending}
              >
                {creation.isPending ? "Création…" : "Créer le projet"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <AlertDialog open={confirmerQuitter} onOpenChange={setConfirmerQuitter}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Quitter le formulaire ?</AlertDialogTitle>
            <AlertDialogDescription>
              Le projet ne sera pas créé et les informations saisies seront
              perdues.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Continuer la saisie</AlertDialogCancel>
            <AlertDialogAction onClick={fermer}>Quitter</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
