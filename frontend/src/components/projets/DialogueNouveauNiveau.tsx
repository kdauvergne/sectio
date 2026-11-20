import { useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { revalidateLogic, useForm } from "@tanstack/react-form";
import { Check } from "lucide-react";
import { creerNiveau } from "@/api/projets";
import { ChampMPa } from "@/components/formulaires/ChampMPa";
import { ConfirmationQuitter } from "@/components/formulaires/ConfirmationQuitter";
import { EncartHypotheses } from "@/components/formulaires/EncartHypotheses";
import { ErreurChamp } from "@/components/formulaires/ErreurChamp";
import { SelectExposition } from "@/components/formulaires/SelectExposition";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
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
  focaliserPremiereErreur,
  resumeHypotheses,
  suggestionsNiveaux,
} from "@/lib/formulaires";
import { schemaHypotheses, schemaNouveauNiveau } from "@/schemas/projet";
import type { BatimentDetail } from "@/types/api";

const ID_FORMULAIRE = "form-nouveau-niveau";

type Props = {
  batiment: BatimentDetail;
  nomProjet: string;
  ouvert: boolean;
  onOuvertChange: (ouvert: boolean) => void;
};

/** À monter avec `key={batiment.id}` : les valeurs initiales viennent du bâtiment. */
export function DialogueNouveauNiveau({
  batiment,
  nomProjet,
  ouvert,
  onOuvertChange,
}: Props) {
  const queryClient = useQueryClient();
  const champNom = useRef<HTMLInputElement>(null);
  const [confirmerQuitter, setConfirmerQuitter] = useState(false);
  const [enchainer, setEnchainer] = useState(false);
  const [niveauxCrees, setNiveauxCrees] = useState<string[]>([]);

  const hypothesesBatimentValides =
    schemaHypotheses.safeParse(batiment).success;
  const [deplie, setDeplie] = useState(!hypothesesBatimentValides);
  const [deplieParClic, setDeplieParClic] = useState(false);

  const nomsExistants = batiment.niveaux.map((niveau) => niveau.nom);
  const schema = schemaNouveauNiveau(batiment.nom, nomsExistants);
  const ordre =
    batiment.niveaux.length > 0
      ? Math.max(...batiment.niveaux.map((niveau) => niveau.ordre)) + 1
      : 0;

  const valeursInitiales = {
    nom: "",
    fck: batiment.fck,
    fyk: batiment.fyk,
    classe_exposition: batiment.classe_exposition,
  };

  const creation = useMutation({
    mutationFn: creerNiveau,
    // Attendre la liste à jour : noms pris et ordre du niveau suivant.
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });

  const formNiveau = useForm({
    defaultValues: valeursInitiales,
    validationLogic: revalidateLogic(),
    validators: { onDynamic: schema },
    onSubmit: async ({ value }) => {
      const niveau = await creation.mutateAsync({
        ...schema.parse(value),
        batiment: batiment.id,
        ordre,
      });
      if (enchainer) {
        setNiveauxCrees((crees) => [...crees, niveau.nom]);
        formNiveau.reset({ ...value, nom: "" });
        creation.reset();
        champNom.current?.focus();
      } else {
        fermer();
      }
    },
    onSubmitInvalid: () => focaliserPremiereErreur(ID_FORMULAIRE),
  });

  function fermer() {
    formNiveau.reset(valeursInitiales);
    creation.reset();
    setDeplie(!hypothesesBatimentValides);
    setDeplieParClic(false);
    setNiveauxCrees([]);
    setEnchainer(false);
    setConfirmerQuitter(false);
    onOuvertChange(false);
  }

  function demanderFermeture() {
    if (!formNiveau.state.isDefaultValue) setConfirmerQuitter(true);
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
              Nouveau niveau
            </DialogTitle>
            <DialogDescription className="info">
              {batiment.nom} · {nomProjet}
            </DialogDescription>
            {niveauxCrees.length > 0 && (
              <p
                role="status"
                className="info-carte mt-1 flex items-start gap-1.5 text-muted-foreground"
              >
                <Check className="mt-0.5 size-3.5 shrink-0 text-foreground" />
                <span>
                  {new Intl.ListFormat("fr", { type: "conjunction" }).format(
                    niveauxCrees,
                  )}{" "}
                  {niveauxCrees.length > 1 ? "créés" : "créé"}
                </span>
              </p>
            )}
          </DialogHeader>

          <form
            id={ID_FORMULAIRE}
            noValidate
            onSubmit={(e) => {
              e.preventDefault();
              formNiveau.handleSubmit();
            }}
          >
            <FieldGroup className="gap-5">
              <formNiveau.Field
                name="nom"
                children={(field) => {
                  const estInvalide = !field.state.meta.isValid;
                  return (
                    <Field data-invalid={estInvalide}>
                      <FieldLabel htmlFor={field.name}>
                        Nom du niveau
                      </FieldLabel>
                      <div
                        className="flex flex-wrap gap-1.5"
                        role="group"
                        aria-label="Noms proposés"
                      >
                        {suggestionsNiveaux(nomsExistants).map((suggestion) => (
                          <Button
                            key={suggestion}
                            type="button"
                            variant="outline"
                            size="xs"
                            className="font-mono text-foreground"
                            onClick={() => {
                              field.handleChange(suggestion);
                              champNom.current?.focus();
                            }}
                          >
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                      <Input
                        ref={champNom}
                        id={field.name}
                        name={field.name}
                        autoFocus
                        autoComplete="off"
                        className="font-mono"
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

              <formNiveau.Subscribe
                selector={(etat) => etat.values}
                children={(valeurs) => (
                  <EncartHypotheses
                    source="bâtiment"
                    cible="niveau"
                    resume={resumeHypotheses(valeurs)}
                    deplie={deplie}
                    onModifier={() => {
                      setDeplie(true);
                      setDeplieParClic(true);
                    }}
                  >
                    <formNiveau.Field
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
                            field.state.value !== batiment.fck
                              ? `Bâtiment : ${batiment.fck}`
                              : undefined
                          }
                        />
                      )}
                    />
                    <formNiveau.Field
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
                            field.state.value !== batiment.fyk
                              ? `Bâtiment : ${batiment.fyk}`
                              : undefined
                          }
                        />
                      )}
                    />
                    <formNiveau.Field
                      name="classe_exposition"
                      children={(field) => (
                        <SelectExposition
                          id={field.name}
                          valeur={field.state.value}
                          onChange={field.handleChange}
                          onBlur={field.handleBlur}
                          erreurs={field.state.meta.errors}
                          aide={
                            field.state.value !== batiment.classe_exposition
                              ? `Bâtiment : ${batiment.classe_exposition || "—"}`
                              : undefined
                          }
                        />
                      )}
                    />
                  </EncartHypotheses>
                )}
              />

              {creation.isError && (
                <p className="info-carte text-destructive">
                  Impossible de créer le niveau. Réessayez.
                </p>
              )}
            </FieldGroup>
          </form>

          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <Field orientation="horizontal" className="w-auto">
              <Checkbox
                id="enchainer-niveau"
                checked={enchainer}
                onCheckedChange={(coche) => setEnchainer(coche === true)}
              />
              <FieldLabel htmlFor="enchainer-niveau" className="font-normal">
                Enchaîner un autre niveau
              </FieldLabel>
            </Field>
            <div className="flex flex-col-reverse gap-2 sm:flex-row">
              <Button
                type="button"
                variant="outline"
                onClick={demanderFermeture}
              >
                {niveauxCrees.length > 0 ? "Terminer" : "Annuler"}
              </Button>
              <Button
                type="submit"
                form={ID_FORMULAIRE}
                disabled={creation.isPending}
              >
                {creation.isPending ? "Création…" : "Créer le niveau"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <ConfirmationQuitter
        ouvert={confirmerQuitter}
        onOuvertChange={setConfirmerQuitter}
        onQuitter={fermer}
        consequence="Le niveau ne sera pas créé"
      />
    </>
  );
}
