import { useParams } from "react-router-dom";

import { useQuery, skipToken } from "@tanstack/react-query";
import { recupererProjet } from "@/api/projets";
import { Skeleton } from "@/components/ui/skeleton";

export function DetailProjet() {
  const { id } = useParams();
  const {
    data: projet,
    isPending,
    isError,
  } = useQuery({
    queryKey: ["projet", id],
    enabled: !!id,
    queryFn: id ? () => recupererProjet(id) : skipToken,
  });
  return (
    <div>
      <div className="grid gap-4 max-w-2xl mx-5 ">
        <h1 className="text-2xl font-semibold mb-6">{projet?.nom}</h1>
      </div>

      <div className="grid grid-cols-3 gap-4 xl:grid-cols-5">
        {isPending &&
          Array.from({ length: 3 }, (_, index) => (
            <Skeleton
              key={index}
              className="my-5 h-40 w-full max-w-xs rounded-xl"
            />
          ))}

        {isError && (
          <p className="text-sm text-destructive">
            Impossible de charger le projet.
          </p>
        )}

        {!isPending && !isError && <p>{projet?.description}</p>}
      </div>
      <h2 className="text-xl font-semibold mt-10 mb-4">Bâtiments</h2>
    </div>
  );
}
