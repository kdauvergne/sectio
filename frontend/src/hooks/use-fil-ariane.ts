import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import type { ElementFilAriane } from "@/components/layout/FilAriane";

type ContexteLayout = {
  setFilAriane: (elements: ElementFilAriane[]) => void;
};

/** Fil d'Ariane de la page, affiché dans le header. */
export function useFilAriane(elements: ElementFilAriane[]) {
  const { setFilAriane } = useOutletContext<ContexteLayout>();
  const cle = JSON.stringify(elements);

  useEffect(() => {
    setFilAriane(JSON.parse(cle));
    return () => setFilAriane([]);
  }, [cle, setFilAriane]);
}
