import { useSearchParams } from "react-router-dom";
import * as React from "react";

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

import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function ReinitialiserMotDePasse() {
  const [searchParams] = useSearchParams();
  const uid = searchParams.get("uid");
  const token = searchParams.get("token");

  const [isPasswordVisible, setIsPasswordVisible] = React.useState(false);
  const [isConfirmPasswordVisible, setIsConfirmPasswordVisible] =
    React.useState(false);
  const [isSubmitted, setIsSubmitted] = React.useState(false);

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitted(true);
  }

  const togglePasswordVisibility = () => {
    setIsPasswordVisible(!isPasswordVisible);
  };

  const toggleConfirmPasswordVisibility = () => {
    setIsConfirmPasswordVisible(!isConfirmPasswordVisible);
  };

  return (
    <div className="grid min-h-svh place-items-center">
      <div className="w-full max-w-sm">
        <Card className="m-auto max-w-md bg-white ring-0">
          <CardHeader className="space-y-1">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
              <LockIcon className="text-primary h-6 w-6" />
            </div>
            <CardTitle className="text-center text-2xl">
              Reset Password
            </CardTitle>
            <CardDescription className="text-center">
              Create a new password for your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isSubmitted ? (
              <Alert className="bg-green-50 text-green-800 dark:bg-green-900 dark:text-green-300">
                <AlertDescription>
                  Votre mot de passe a bien été réinitialisé. Vous pouvez
                  maintenant{" "}
                  <a href="#" className="font-medium underline">
                    accéder à votre compte
                  </a>{" "}
                  avec vos identifiants.
                </AlertDescription>
              </Alert>
            ) : (
              <form onSubmit={onSubmit} className="space-y-4">
                <FieldGroup>
                  <Field>
                    <FieldLabel htmlFor="password">
                      Nouveau mot de passe
                    </FieldLabel>
                    <div className="relative">
                      <Input
                        id="password"
                        placeholder="••••••••••••••••"
                        type={isPasswordVisible ? "text" : "password"}
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
                          Toggle password visibility
                        </span>
                      </Button>
                    </div>
                    <FieldDescription>
                      Le mot de passe doit avoir au minimum 8 caractères,
                      contenir des majuscules, des minuscules, et des symboles.
                    </FieldDescription>
                  </Field>
                  <Field>
                    <FieldLabel htmlFor="confirmPassword">
                      Confirmer mot de passe
                    </FieldLabel>
                    <div className="relative">
                      <Input
                        id="confirmPassword"
                        placeholder="••••••••••••••••"
                        type={isConfirmPasswordVisible ? "text" : "password"}
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
                          Afficher le mot de passe
                        </span>
                      </Button>
                    </div>
                  </Field>
                </FieldGroup>
                <Button type="submit" className="w-full">
                  Réinitialiser le mot de passe
                </Button>
              </form>
            )}
          </CardContent>
          <CardFooter className="flex justify-center">
            <p className="text-muted-foreground text-sm">
              Vous vous souvenez de votre mot de passe ?{" "}
              <a href="#" className="text-primary underline">
                Connectez-vous
              </a>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
