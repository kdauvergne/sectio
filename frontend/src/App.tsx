import { CarteProjet } from "@/components/projets/CarteProjet";
import { PROJETS_DEMO } from "@/donnees-demo";

function App() {
  return (
    <div className="grid gap-4 max-w-2xl m-5">
      <h1 className="text-2xl font-semibold mb-6">Projets</h1>

      {PROJETS_DEMO.map((projet) => (
        <CarteProjet key={projet.id} projet={projet} />
      ))}
    </div>
  );
}

export default App;
