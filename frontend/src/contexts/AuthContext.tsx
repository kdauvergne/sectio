import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { connexion, deconnexion, recupererMonCompte } from "@/api/auth";
import type { Utilisateur } from "@/types/api";
import { useNavigate } from "react-router";
import { setOnSessionExpired } from "@/lib/api";

type ValeurContexteAuth = {
  utilisateur: Utilisateur | null;
  chargementInitial: boolean;
  seConnecter: (email: string, password: string) => Promise<void>;
  seDeconnecter: () => Promise<void>;
};

const ContexteAuth = createContext<ValeurContexteAuth | null>(null);

export function ProviderAuth({ children }: { children: ReactNode }) {
  const [utilisateur, setUtilisateur] = useState<Utilisateur | null>(null);
  const [chargementInitial, setChargementInitial] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    recupererMonCompte()
      .then((compte) => setUtilisateur(compte))
      .catch(() => setUtilisateur(null))
      .finally(() => setChargementInitial(false));
  }, []);

  useEffect(() => {
    setOnSessionExpired(() => {
      setUtilisateur(null);
      navigate("/connexion", { replace: true });
    });
  }, [navigate]);

  async function seConnecter(email: string, password: string) {
    await connexion(email, password);
    setUtilisateur(await recupererMonCompte());
  }

  async function seDeconnecter() {
    await deconnexion();
    setUtilisateur(null);
  }

  return (
    <ContexteAuth.Provider
      value={{ utilisateur, chargementInitial, seConnecter, seDeconnecter }}
    >
      {children}
    </ContexteAuth.Provider>
  );
}

export function useAuth() {
  const contexte = useContext(ContexteAuth);
  if (!contexte) {
    throw new Error(
      "useAuth doit être utilisé à l'intérieur d'un ProviderAuth",
    );
  }
  return contexte;
}
