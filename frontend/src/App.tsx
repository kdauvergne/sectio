import { useState } from "react";
import { CarteProjet } from "@/components/projets/CarteProjet";
import { PROJETS_DEMO } from "@/donnees-demo";
import { POTEAUX_DEMO } from "@/donnees-demo";
import { BarreRecherche } from "./components/projets/BarreRecherche";
import { TableauPoteaux } from "./components/poteaux/TableauPoteaux";
import { AppLayout } from "@/components/layout/AppLayout";

function App() {
  const [recherche, setRecherche] = useState("");

  const projetFiltres = PROJETS_DEMO.filter((projet) =>
    projet.nom.toLowerCase().includes(recherche.toLowerCase()),
  );

  return (
    <AppLayout>
      <div className="grid gap-4 max-w-2xl mx-5 ">
        <h1 className="text-2xl font-semibold mb-6">Tableau de bord</h1>
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
        <h2 className="text-xl font-semibold mt-10 mb-4">Poteaux du niveau</h2>
        <TableauPoteaux poteaux={POTEAUX_DEMO} />
      </div>
    </AppLayout>
  );
}

export default App;
