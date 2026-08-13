import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { TableauDeBord } from "@/pages/TableauDeBord";
import { Connexion } from "@/pages/Connexion";

function App() {
  return (
    <Routes>
      <Route path="/connexion" element={<Connexion />} />

      <Route element={<AppLayout />}>
        <Route path="/" element={<TableauDeBord />} />
        <Route path="/projets" element={<div>Projets</div>} />
        <Route path="/projets/:id" element={<div>Détail projet</div>} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
