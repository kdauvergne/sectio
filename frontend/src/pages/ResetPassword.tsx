import * as React from "react";
import { useSearchParams } from "react-router-dom";

import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { EyeIcon, EyeOffIcon, LockIcon } from "lucide-react";

import { resetPassword } from "@/api/auth";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { schemaNouveauMotDePasse } from "@/schemas/auth";
import { useForm } from "@tanstack/react-form";
import { useState } from "react";
import { Link } from "react-router-dom";

export function ReinitialiserMotDePasse() {
  const [searchParams] = useSearchParams();
  const uid = searchParams.get("uid");
  const token = searchParams.get("token");

  const [isPasswordVisible, setIsPasswordVisible] = React.useState(false);
  const [isConfirmPasswordVisible, setIsConfirmPasswordVisible] =
    React.useState(false);
  const [isSubmitted, setIsSubmitted] = React.useState(false);
  const [erreurServeur, setErreurServeur] = useState<string | null>(null);

  const togglePasswordVisibility = () => {
    setIsPasswordVisible(!isPasswordVisible);
  };

  const toggleConfirmPasswordVisibility = () => {
    setIsConfirmPasswordVisible(!isConfirmPasswordVisible);
  };

  const formResetPwd = useForm({
    defaultValues: { new_password: "", confirmPassword: "" },
    validators: { onSubmit: schemaNouveauMotDePasse },
    onSubmit: async ({ value }) => {
      if (!uid || !token) return;

      setErreurServeur(null);
      try {
        await resetPassword({
          uid: uid,
          token: token,
          new_password: value.new_password,
        });
        setIsSubmitted(true);
      } catch {
        setErreurServeur("Une erreur est survenue. Réessayez.");
      }
    },
  });

  if (!uid || !token) {
    return (
      <Alert className="bg-green-50 text-green-800 dark:bg-green-900 dark:text-green-300">
        Ce lien de réinitialisation est incomplet ou invalide.
        <Link to="/connexion" className="font-medium underline">
          Redemandez un lien.
        </Link>
      </Alert>
    );
  }

  return (
    <div className="grid min-h-svh place-items-center">
      <div className="w-full max-w-sm">
        <Card className="m-auto max-w-md bg-white ring-0">
          <CardHeader className="space-y-1">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
              <LockIcon className="text-primary h-6 w-6" />
            </div>
            <CardTitle className="text-center text-2xl">
              Réinitialisez votre mot de passe
            </CardTitle>
            <CardDescription className="text-center">
              Créez un nouveau mot de passe
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isSubmitted ? (
              <Alert className="bg-green-50 text-green-800 dark:bg-green-900 dark:text-green-300">
                <AlertDescription>
                  Votre mot de passe a bien été réinitialisé. Vous pouvez
                  maintenant{" "}
                  <Link to="/connexion" className="font-medium underline">
                    accéder à votre compte
                  </Link>{" "}
                  avec vos identifiants.
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
                    name="new_password"
                    children={(field) => {
                      const estInvalide =
                        field.state.meta.isTouched && !field.state.meta.isValid;
                      return (
                        <Field data-invalid={estInvalide}>
                          <FieldLabel htmlFor={field.name}>
                            Nouveau mot de passe
                          </FieldLabel>
                          <div className="relative">
                            <Input
                              id={field.name}
                              name={field.name}
                              placeholder="••••••••••••••••"
                              type={isPasswordVisible ? "text" : "password"}
                              autoComplete="new-password"
                              value={field.state.value}
                              onBlur={field.handleBlur}
                              onChange={(e) =>
                                field.handleChange(e.target.value)
                              }
                              aria-invalid={estInvalide}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="text-muted-foreground absolute top-0 right-0 h-full px-3 py-2"
                              onClick={togglePasswordVisibility}
                            >
                              {isPasswordVisible ? (
                                <EyeOffIcon className="h-4 w-4" />
                              ) : (
                                <EyeIcon className="h-4 w-4" />
                              )}
                              <span className="sr-only">
                                Afficher le mot de passe
                              </span>
                            </Button>
                          </div>
                          {estInvalide && (
                            <FieldError errors={field.state.meta.errors} />
                          )}
                        </Field>
                      );
                    }}
                  />
                  <formResetPwd.Field
                    name="confirmPassword"
                    children={(field) => {
                      const estInvalide =
                        field.state.meta.isTouched && !field.state.meta.isValid;
                      return (
                        <Field data-invalid={estInvalide}>
                          <FieldLabel htmlFor={field.name}>
                            Confirmer le mot de passe
                          </FieldLabel>
                          <div className="relative">
                            <Input
                              id={field.name}
                              name={field.name}
                              placeholder="••••••••••••••••"
                              type={
                                isConfirmPasswordVisible ? "text" : "password"
                              }
                              autoComplete="new-password"
                              value={field.state.value}
                              onBlur={field.handleBlur}
                              onChange={(e) =>
                                field.handleChange(e.target.value)
                              }
                              aria-invalid={estInvalide}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="text-muted-foreground absolute top-0 right-0 h-full px-3 py-2"
                              onClick={toggleConfirmPasswordVisibility}
                            >
                              {isConfirmPasswordVisible ? (
                                <EyeOffIcon className="h-4 w-4" />
                              ) : (
                                <EyeIcon className="h-4 w-4" />
                              )}
                              <span className="sr-only">
                                Afficher la confirmation du mot de passe
                              </span>
                            </Button>
                          </div>
                          {estInvalide && (
                            <FieldError errors={field.state.meta.errors} />
                          )}
                        </Field>
                      );
                    }}
                  />
                </FieldGroup>
                {erreurServeur && (
                  <p role="alert" className="text-destructive text-sm">
                    {erreurServeur}
                  </p>
                )}
                <Button type="submit" className="w-full mt-5">
                  Réinitialiser le mot de passe
                </Button>
              </form>
            )}
          </CardContent>
          <CardFooter className="flex justify-center">
            <p className="text-muted-foreground text-sm">
              Vous vous souvenez de votre mot de passe ?{" "}
              <Link to="/connexion" className="text-primary underline">
                Connectez-vous
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
