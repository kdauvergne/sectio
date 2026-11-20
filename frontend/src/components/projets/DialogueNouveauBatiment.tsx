import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { revalidateLogic, useForm } from "@tanstack/react-form";
import { creerBatiment } from "@/api/projets";
import { ChampMPa } from "@/components/formulaires/ChampMPa";
import { ConfirmationQuitter } from "@/components/formulaires/ConfirmationQuitter";
import { EncartHypotheses } from "@/components/formulaires/EncartHypotheses";
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
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  compterErreurs,
  focaliserPremiereErreur,
  resumeHypotheses,
} from "@/lib/formulaires";
import { schemaHypotheses, schemaNouveauBatiment } from "@/schemas/projet";
import type { ProjetDetail } from "@/types/api";

const ID_FORMULAIRE = "form-nouveau-batiment";

type Props = {
  projet: ProjetDetail;
  ouvert: boolean;
  onOuvertChange: (ouvert: boolean) => void;
};

export function DialogueNouveauBatiment({
  projet,
  ouvert,
  onOuvertChange,
}: Props) {
  const queryClient = useQueryClient();
  const [confirmerQuitter, setConfirmerQuitter] = useState(false);

  // Hypothèses du projet hors du domaine de la méthode : à corriger tout de suite.
  const hypothesesProjetValides = schemaHypotheses.safeParse(projet).success;
  const [deplie, setDeplie] = useState(!hypothesesProjetValides);
  const [deplieParClic, setDeplieParClic] = useState(false);

  const schema = schemaNouveauBatiment(
    projet.nom,
    projet.batiments.map((batiment) => batiment.nom),
  );

  const creation = useMutation({
    mutationFn: creerBatiment,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["projets"] });
      fermer();
    },
  });

  const formBatiment = useForm({
    defaultValues: {
      nom: "",
      fck: projet.fck,
      fyk: projet.fyk,
      classe_exposition: projet.classe_exposition,
    },
    validationLogic: revalidateLogic(),
    validators: { onDynamic: schema },
    onSubmit: async ({ value }) => {
      await creation.mutateAsync({ ...schema.parse(value), projet: projet.id });
    },
    onSubmitInvalid: () => focaliserPremiereErreur(ID_FORMULAIRE),
  });

  function fermer() {
    formBatiment.reset();
    creation.reset();
    setDeplie(!hypothesesProjetValides);
    setDeplieParClic(false);
    setConfirmerQuitter(false);
    onOuvertChange(false);
  }

  function demanderFermeture() {
    if (!formBatiment.state.isDefaultValue) setConfirmerQuitter(true);
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
              Nouveau bâtiment
            </DialogTitle>
            <DialogDescription className="info">{projet.nom}</DialogDescription>
          </DialogHeader>

          <form
            id={ID_FORMULAIRE}
            noValidate
            onSubmit={(e) => {
              e.preventDefault();
              formBatiment.handleSubmit();
            }}
          >
            <FieldGroup className="gap-5">
              <formBatiment.Field
                name="nom"
                children={(field) => {
                  const estInvalide = !field.state.meta.isValid;
                  return (
                    <Field data-invalid={estInvalide}>
                      <FieldLabel htmlFor={field.name}>
                        Nom du bâtiment
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

              <formBatiment.Subscribe
                selector={(etat) => etat.values}
                children={(valeurs) => (
                  <EncartHypotheses
                    source="projet"
                    cible="bâtiment"
                    resume={resumeHypotheses(valeurs)}
                    deplie={deplie}
                    onModifier={() => {
                      setDeplie(true);
                      setDeplieParClic(true);
                    }}
                  >
                    <formBatiment.Field
                      name="fck"
                      children={(field) => (
                        <ChampMPa
                          id={field.name}
                          libelle="fck — béton"
                          autoFocus={deplieParClic}
                          valeur={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          erreurs={field.state.meta.errors}
                          aide={
                            field.state.value !== projet.fck
                              ? `Projet : ${projet.fck}`
                              : undefined
                          }
                        />
                      )}
                    />
                    <formBatiment.Field
                      name="fyk"
                      children={(field) => (
                        <ChampMPa
                          id={field.name}
                          libelle="fyk — acier"
                          valeur={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          erreurs={field.state.meta.errors}
                          aide={
                            field.state.value !== projet.fyk
                              ? `Projet : ${projet.fyk}`
                              : undefined
                          }
                        />
                      )}
                    />
                    <formBatiment.Field
                      name="classe_exposition"
                      children={(field) => (
                        <SelectExposition
                          id={field.name}
                          valeur={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          erreurs={field.state.meta.errors}
                          aide={
                            field.state.value !== projet.classe_exposition
                              ? `Projet : ${projet.classe_exposition || "—"}`
                              : undefined
                          }
                        />
                      )}
                    />
                  </EncartHypotheses>
                )}
              />
            </FieldGroup>
          </form>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
            <formBatiment.Subscribe
              selector={(etat) => compterErreurs(etat.fieldMeta)}
              children={(nbErreurs) => (
                <IndicationPied
                  erreurEnvoi={
                    creation.isError
                      ? "Impossible de créer le bâtiment. Réessayez."
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
                {creation.isPending ? "Création…" : "Créer le bâtiment"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <ConfirmationQuitter
        ouvert={confirmerQuitter}
        onOuvertChange={setConfirmerQuitter}
        onQuitter={fermer}
        consequence="Le bâtiment ne sera pas créé"
      />
    </>
  );
}
