import { AppLayout } from "@/components/layout/AppLayout";
import { Connexion } from "@/pages/Connexion";
import { ReinitialiserMotDePasse } from "@/pages/ResetPassword";

import { TableauDeBord } from "@/pages/TableauDeBord";
import { Route, Routes } from "react-router-dom";
import { RouteProtegee } from "./components/RouteProtegee";

function App() {
  return (
    <Routes>
      <Route path="/connexion" element={<Connexion />} />
      <Route path="/reset-password" element={<ReinitialiserMotDePasse />} />

      <Route element={<RouteProtegee />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<TableauDeBord />} />
          <Route path="/projets" element={<div>Projets</div>} />
          <Route path="/projets/:id" element={<div>Détail projet</div>} />
        </Route>
      </Route>

      <Route path="*" element={<h1 className="p-8">Page introuvable</h1>} />
    </Routes>
  );
}

export default App;
