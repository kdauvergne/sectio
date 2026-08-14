import { Button } from "@/components/ui/button";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { schemaConnexion } from "@/schemas/auth";
import { useForm } from "@tanstack/react-form";
import { Square } from "lucide-react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export function Connexion() {
  const { seConnecter } = useAuth();
  const navigate = useNavigate();
  const emplacement = useLocation();
  const [erreurServeur, setErreurServeur] = useState<string | null>(null);

  const destination = (emplacement.state as { de?: string } | null)?.de ?? "/";

  const form = useForm({
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
              form.handleSubmit();
            }}
          >
            <FieldGroup>
              <form.Field
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
              <form.Field
                name="password"
                children={(field) => {
                  const estInvalide =
                    field.state.meta.isTouched && !field.state.meta.isValid;
                  return (
                    <Field data-invalid={estInvalide}>
                      <FieldLabel htmlFor={field.name}>Mot de passe</FieldLabel>
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
              <a
                href="#"
                className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
              >
                Mot de passe oublié ?
              </a>
              <form.Subscribe
                selector={(etat) => etat.isSubmitting}
                children={(envoiEnCours) => (
                  <Button
                    type="submit"
                    className="w-full"
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
    </div>
  );
}
