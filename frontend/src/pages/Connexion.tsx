import * as React from "react";
import { Button } from "@/components/ui/button";

import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { schemaConnexion, schemaResetPwd } from "@/schemas/auth";
import { useForm } from "@tanstack/react-form";
import { LockIcon, Square } from "lucide-react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { demandeResetPwd } from "@/api/auth";

export function Connexion() {
  const { seConnecter } = useAuth();
  const navigate = useNavigate();
  const emplacement = useLocation();
  const [erreurServeur, setErreurServeur] = useState<string | null>(null);

  const destination = (emplacement.state as { de?: string } | null)?.de ?? "/";

  const formConnexion = useForm({
    defaultValues: { email: "", password: "" },
    validators: { onSubmit: schemaConnexion },
    onSubmit: async ({ value }) => {
      setErreurServeur(null);
      try {
        await seConnecter(value.email, value.password);
        navigate(destination, { replace: true });
      } catch {
        setErreurServeur("E-mail ou mot de passe incorrect.");
      }
    },
  });

  const formResetPwd = useForm({
    defaultValues: { email: "" },
    validators: { onSubmit: schemaResetPwd },
    onSubmit: async ({ value }) => {
      setErreurServeur(null);
      try {
        await demandeResetPwd(value.email);
        setIsSubmitted(true);
      } catch {
        setErreurServeur("Une erreur est survenue. Réessayez.");
      }
    },
  });

  const [vue, setVue] = useState<"connexion" | "resetPwd">("connexion");

  const [isSubmitted, setIsSubmitted] = React.useState(false);

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitted(true);
  }

  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="bg-secondary text-secondary-foreground hidden flex-col justify-between p-10 lg:flex">
        <div className="flex items-center gap-2 text-lg font-medium">
          <Square className="size-5" />
          <strong>Sectio</strong>
        </div>

        <blockquote className="space-y-3">
          <p className="text-4xl leading-snug font-bold">
            Le dimensionnement n'a jamais été aussi facile.
          </p>
          <footer className="text-sm opacity-70">
            Dimensionnement de poteaux en béton armé - Eurocode 2
          </footer>
        </blockquote>
      </div>
      {vue === "connexion" ? (
        <>
          <div className="flex items-center justify-center p-6 lg:p-10">
            <div className="w-full max-w-sm">
              <div className="text-center mb-8 space-y-2 ">
                <p className="text-3xl font-semibold">Connectez-vous</p>
                <p className="text-muted-foreground text-sm">
                  Reprenez vos projets et notes de calculs en cours.{" "}
                </p>
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  formConnexion.handleSubmit();
                }}
              >
                <FieldGroup>
                  <formConnexion.Field
                    name="email"
                    children={(field) => {
                      const estInvalide =
                        field.state.meta.isTouched && !field.state.meta.isValid;
                      return (
                        <Field data-invalid={estInvalide}>
                          <FieldLabel htmlFor={field.name}>
                            Adresse e-mail
                          </FieldLabel>
                          <Input
                            id={field.name}
                            name={field.name}
                            type="email"
                            autoComplete="email"
                            value={field.state.value}
                            onBlur={field.handleBlur}
                            onChange={(e) => field.handleChange(e.target.value)}
                            aria-invalid={estInvalide}
                          />
                          {estInvalide && (
                            <FieldError errors={field.state.meta.errors} />
                          )}
                        </Field>
                      );
                    }}
                  />
                  <formConnexion.Field
                    name="password"
                    children={(field) => {
                      const estInvalide =
                        field.state.meta.isTouched && !field.state.meta.isValid;
                      return (
                        <Field data-invalid={estInvalide}>
                          <FieldLabel htmlFor={field.name}>
                            Mot de passe
                          </FieldLabel>
                          <Input
                            id={field.name}
                            name={field.name}
                            type="password"
                            autoComplete="current-password"
                            value={field.state.value}
                            onBlur={field.handleBlur}
                            onChange={(e) => field.handleChange(e.target.value)}
                            aria-invalid={estInvalide}
                          />
                          {estInvalide && (
                            <FieldError errors={field.state.meta.errors} />
                          )}
                        </Field>
                      );
                    }}
                  />
                  {erreurServeur && (
                    <p role="alert" className="text-destructive text-sm">
                      {erreurServeur}
                    </p>
                  )}
                  <Button
                    type="button"
                    variant={"link"}
                    onClick={() => setVue("resetPwd")}
                    className="ml-auto text-secondary inline-block text-sm underline-offset-4 hover:underline cursor-pointer"
                  >
                    Mot de passe oublié ?
                  </Button>
                  <formConnexion.Subscribe
                    selector={(etat) => etat.isSubmitting}
                    children={(envoiEnCours) => (
                      <Button
                        type="submit"
                        className="w-full cursor-pointer"
                        disabled={envoiEnCours}
                      >
                        {envoiEnCours ? "Connexion..." : "Se connecter"}
                      </Button>
                    )}
                  />
                </FieldGroup>
              </form>
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="m-auto w-full max-w-sm">
            <Card className="m-auto max-w-md bg-white ring-0">
              <CardHeader className="space-y-1">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
                  <LockIcon className="text-primary h-6 w-6" />
                </div>
                <CardTitle className="text-center text-2xl">
                  Demande de réinitialisation du mot de passe
                </CardTitle>
                <CardDescription className="text-center">
                  Nous vous enverrons un lien de réinitialisation
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isSubmitted ? (
                  <Alert className="bg-green-50 text-green-800 dark:bg-green-900 dark:text-green-300">
                    <AlertDescription>
                      Si votre email correspond à un compte utilisateur, votre
                      demande de réinitialisation a bien été envoyé. Vérifiez
                      vos spams.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      formResetPwd.handleSubmit();
                    }}
                  >
                    <FieldGroup>
                      <formResetPwd.Field
                        name="email"
                        children={(field) => {
                          const estInvalide =
                            field.state.meta.isTouched &&
                            !field.state.meta.isValid;
                          return (
                            <Field data-invalid={estInvalide}>
                              <FieldLabel htmlFor={field.name}>
                                Adresse e-mail
                              </FieldLabel>
                              <Input
                                id={field.name}
                                name={field.name}
                                type="email"
                                autoComplete="email"
                                value={field.state.value}
                                onBlur={field.handleBlur}
                                onChange={(e) =>
                                  field.handleChange(e.target.value)
                                }
                                aria-invalid={estInvalide}
                              />
                              {estInvalide && (
                                <FieldError errors={field.state.meta.errors} />
                              )}
                            </Field>
                          );
                        }}
                      />

                      {erreurServeur && (
                        <p role="alert" className="text-destructive text-sm">
                          {erreurServeur}
                        </p>
                      )}

                      <formResetPwd.Subscribe
                        selector={(etat) => etat.isSubmitting}
                        children={(envoiEnCours) => (
                          <Button
                            type="submit"
                            className="w-full cursor-pointer"
                            disabled={envoiEnCours}
                          >
                            {envoiEnCours
                              ? "Chargement..."
                              : "Envoyer la demande de réinitialisation"}
                          </Button>
                        )}
                      />
                    </FieldGroup>
                  </form>
                )}
              </CardContent>
              <CardFooter className="flex justify-center">
                <p className="text-muted-foreground text-sm">
                  Vous vous souvenez de votre mot de passe ?{" "}
                  <Button
                    variant="link"
                    onClick={() => setVue("connexion")}
                    className="text-primary underline cursor-pointer m-0 p-0"
                  >
                    Connectez-vous
                  </Button>
                </p>
              </CardFooter>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
