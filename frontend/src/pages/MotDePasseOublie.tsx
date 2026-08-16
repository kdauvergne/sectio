import { demandeResetPwd } from "@/api/auth";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { schemaResetPwd } from "@/schemas/auth";
import { useForm } from "@tanstack/react-form";
import { LockIcon } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";

import { Input } from "@/components/ui/input";

export function MotDePasseOublie() {
  const [erreurServeur, setErreurServeur] = useState<string | null>(null);

  const navigate = useNavigate();

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
  const [isSubmitted, setIsSubmitted] = useState(false);
  return (
    <Card className="m-auto max-w-md bg-white ring-0">
      <CardHeader className="space-y-1">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
          <LockIcon className="text-primary h-6 w-6" />
        </div>
        <CardTitle className="text-center text-2xl">
          Réinitialisation du mot de passe
        </CardTitle>
        <CardDescription className="text-center">
          Nous vous enverrons un lien sur votre email lié à votre compte Sectio.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isSubmitted ? (
          <Alert className="bg-green-50 text-green-800 dark:bg-green-900 dark:text-green-300">
            <AlertDescription>
              Votre demande de réinitialisation a bien été envoyé. Si votre
              email correspond à un compte utilisateur, vous avez reçu un lien
              cliquable. Vérifiez vos spams.
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
            onClick={() => navigate("/connexion")}
            className="text-primary underline cursor-pointer m-0 p-0"
          >
            Connectez-vous
          </Button>
        </p>
      </CardFooter>
    </Card>
  );
}
