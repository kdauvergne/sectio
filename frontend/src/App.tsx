import { useState } from "react";
import { CarteProjet } from "@/components/projets/CarteProjet";
import { PROJETS_DEMO } from "@/donnees-demo";
import { BarreRecherche } from "./components/projets/BarreRecherche";

function App() {
  const [recherche, setRecherche] = useState("");

  const projetFiltres = PROJETS_DEMO.filter((projet) =>
    projet.nom.toLowerCase().includes(recherche.toLowerCase()),
  );

  return (
    <div className="grid gap-4 max-w-2xl m-5 mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Projets</h1>
      <div className="mb-6">
        <BarreRecherche valeur={recherche} onChangement={setRecherche} />
      </div>
      {projetFiltres.map((projet) => (
        <CarteProjet key={projet.id} projet={projet} />
      ))}
      {projetFiltres.length === 0 && (
        <p className="text-sm text-muted-foreground">
          Aucun projet ne correspond à « {recherche} ».
        </p>
      )}
    </div>
  );
}

export default App;
