import { Button } from "@/components/ui/button";

import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { schemaConnexion } from "@/schemas/auth";
import { useForm } from "@tanstack/react-form";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

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

  return (
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
                  <FieldLabel htmlFor={field.name}>Adresse e-mail</FieldLabel>
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
          <Button
            type="button"
            variant={"link"}
            onClick={() => navigate("/mot-de-passe-oublie")}
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

          <FieldDescription className="text-center">
            Pas encore de compte ? <Link to="/inscription">Inscrivez-vous</Link>
          </FieldDescription>
        </FieldGroup>
      </form>
    </div>
  );
}
