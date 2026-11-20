import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { revalidateLogic, useForm } from "@tanstack/react-form";
import { creerProjet } from "@/api/projets";
import { ChampMPa } from "@/components/formulaires/ChampMPa";
import { ConfirmationQuitter } from "@/components/formulaires/ConfirmationQuitter";
import { ErreurChamp } from "@/components/formulaires/ErreurChamp";
import { IndicationPied } from "@/components/formulaires/IndicationPied";
import { SelectExposition } from "@/components/formulaires/SelectExposition";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Field, FieldGroup, FieldLabel, FieldSet } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import type { ClasseExposition } from "@/lib/beton";
import { compterErreurs, focaliserPremiereErreur } from "@/lib/formulaires";
import { schemaNouveauProjet } from "@/schemas/projet";

const ID_FORMULAIRE = "form-nouveau-projet";

/** fck = 45 MPa et fyk = 500 MPa : défauts du modèle Projet. */
const VALEURS_INITIALES = {
  nom: "",
  fck: 45,
  fyk: 500,
  classe_exposition: "" as ClasseExposition | "",
};

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
    onSubmitInvalid: () => focaliserPremiereErreur(ID_FORMULAIRE),
  });

  function fermer() {
    formProjet.reset();
    creation.reset();
    setConfirmerQuitter(false);
    onOuvertChange(false);
  }

  /** Échap, Annuler ou clic hors du dialogue : confirmation seulement si la saisie a changé. */
  function demanderFermeture() {
    if (!formProjet.state.isDefaultValue) setConfirmerQuitter(true);
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
                    <formProjet.Field
                      name="fck"
                      children={(field) => (
                        <ChampMPa
                          id={field.name}
                          libelle="fck — béton"
                          valeur={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          erreurs={field.state.meta.errors}
                        />
                      )}
                    />
                    <formProjet.Field
                      name="fyk"
                      children={(field) => (
                        <ChampMPa
                          id={field.name}
                          libelle="fyk — acier"
                          valeur={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          erreurs={field.state.meta.errors}
                        />
                      )}
                    />
                    <formProjet.Field
                      name="classe_exposition"
                      children={(field) => (
                        <SelectExposition
                          id={field.name}
                          valeur={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          erreurs={field.state.meta.errors}
                        />
                      )}
                    />
                  </div>
                </FieldSet>
              </div>
            </FieldGroup>
          </form>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
            <formProjet.Subscribe
              selector={(etat) => compterErreurs(etat.fieldMeta)}
              children={(nbErreurs) => (
                <IndicationPied
                  erreurEnvoi={
                    creation.isError
                      ? "Impossible de créer le projet. Réessayez."
                      : undefined
                  }
                  nbErreurs={nbErreurs}
                />
              )}
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

      <ConfirmationQuitter
        ouvert={confirmerQuitter}
        onOuvertChange={setConfirmerQuitter}
        onQuitter={fermer}
        consequence="Le projet ne sera pas créé"
      />
    </>
  );
}
