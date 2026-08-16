import { Button } from "@/components/ui/button";
import {
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Card,
} from "@/components/ui/card";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { schemaInscription } from "@/schemas/auth";
import { useForm } from "@tanstack/react-form";
import { EyeIcon, EyeOffIcon, User2 } from "lucide-react";
import { Link } from "react-router-dom";

import { inscription } from "@/api/auth";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export function Inscription() {
  const { seConnecter } = useAuth();
  const navigate = useNavigate();

  const [erreurServeur, setErreurServeur] = useState<string | null>(null);

  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isConfirmPasswordVisible, setIsConfirmPasswordVisible] =
    useState(false);

  const togglePasswordVisibility = () => {
    setIsPasswordVisible(!isPasswordVisible);
  };

  const toggleConfirmPasswordVisibility = () => {
    setIsConfirmPasswordVisible(!isConfirmPasswordVisible);
  };

  const form = useForm({
    defaultValues: {
      nom: "",
      prenom: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
    validators: { onSubmit: schemaInscription },

    onSubmit: async ({ value }) => {
      setErreurServeur(null);
      try {
        await inscription({
          email: value.email,
          last_name: value.nom,
          first_name: value.prenom,
          password: value.password,
        });
        await seConnecter(value.email, value.password);
        navigate("/", { replace: true });
      } catch {
        setErreurServeur(
          "Impossible de créer le compte. Vérifiez vos informations.",
        );
      }
    },
  });

  return (
    <div className="w-full max-w-sm">
      <Card className="ring-0 bg-transparent">
        <CardHeader className="space-y-1">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full">
            <User2 className="text-primary h-6 w-6" />
          </div>
          <CardTitle className="text-3xl font-semibold text-center ">
            Inscrivez-vous
          </CardTitle>
          <CardDescription className="text-center mb-4 ">
            Créez un compte pour accéder à Sectio
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Début du form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              form.handleSubmit();
            }}
          >
            <FieldGroup>
              {/* Champ Nom */}
              <form.Field name="nom">
                {(field) => {
                  const estInvalide =
                    field.state.meta.isTouched && !field.state.meta.isValid;
                  return (
                    <Field data-invalid={estInvalide}>
                      <FieldLabel htmlFor={field.name}>Nom</FieldLabel>
                      <Input
                        id={field.name}
                        name={field.name}
                        value={field.state.value}
                        onBlur={field.handleBlur}
                        onChange={(e) => field.handleChange(e.target.value)}
                        aria-invalid={estInvalide}
                        type="text"
                        placeholder="Entrez votre nom"
                        autoComplete="family-name"
                      />
                      {estInvalide && (
                        <FieldError errors={field.state.meta.errors} />
                      )}
                    </Field>
                  );
                }}
              </form.Field>
              {/* Champ Prénom */}
              <form.Field name="prenom">
                {(field) => {
                  const estInvalide =
                    field.state.meta.isTouched && !field.state.meta.isValid;
                  return (
                    <Field data-invalid={estInvalide}>
                      <FieldLabel htmlFor={field.name}>Prénom</FieldLabel>
                      <Input
                        id={field.name}
                        name={field.name}
                        value={field.state.value}
                        onBlur={field.handleBlur}
                        onChange={(e) => field.handleChange(e.target.value)}
                        aria-invalid={estInvalide}
                        type="text"
                        placeholder="Entrez votre prénom"
                        autoComplete="given-name"
                      />
                      {estInvalide && (
                        <FieldError errors={field.state.meta.errors} />
                      )}
                    </Field>
                  );
                }}
              </form.Field>
              {/* Champ Mail */}
              <form.Field name="email">
                {(field) => {
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
                        placeholder="Entrez votre adresse email"
                      />
                      {estInvalide && (
                        <FieldError errors={field.state.meta.errors} />
                      )}
                    </Field>
                  );
                }}
              </form.Field>
              {/* Champ Mot de passe */}
              <form.Field name="password">
                {(field) => {
                  const estInvalide =
                    field.state.meta.isTouched && !field.state.meta.isValid;
                  return (
                    <Field data-invalid={estInvalide}>
                      <FieldLabel htmlFor={field.name}>Mot de passe</FieldLabel>
                      <div className="relative">
                        <Input
                          id={field.name}
                          name={field.name}
                          placeholder="••••••••••••••••"
                          type={isPasswordVisible ? "text" : "password"}
                          autoComplete="new-password"
                          value={field.state.value}
                          onBlur={field.handleBlur}
                          onChange={(e) => field.handleChange(e.target.value)}
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
              </form.Field>
              {/* Champ Confirmation MDP */}
              <form.Field name="confirmPassword">
                {(field) => {
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
                          type={isConfirmPasswordVisible ? "text" : "password"}
                          autoComplete="new-password"
                          value={field.state.value}
                          onBlur={field.handleBlur}
                          onChange={(e) => field.handleChange(e.target.value)}
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
              </form.Field>
              <FieldGroup>
                {erreurServeur && (
                  <p role="alert" className="text-destructive text-sm">
                    {erreurServeur}
                  </p>
                )}
                <Field className="mt-4">
                  <form.Subscribe selector={(state) => state.isSubmitting}>
                    {(isSubmitting) => (
                      <Button type="submit" disabled={isSubmitting}>
                        {isSubmitting ? "Création…" : "Créer un compte"}
                      </Button>
                    )}
                  </form.Subscribe>
                </Field>
                <FieldDescription className="my-10 px-6 text-center">
                  Vous avez déjà un compte ?{" "}
                  <Link to="/connexion">Connectez-vous</Link>
                </FieldDescription>
              </FieldGroup>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
