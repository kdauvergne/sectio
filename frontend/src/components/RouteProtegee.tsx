import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

export function RouteProtegee() {
  const { utilisateur, chargementInitial } = useAuth();
  const emplacement = useLocation();

  if (chargementInitial) {
    return (
      <div className="text-muted-foreground grid min-h-svh place-items-center">
        Chargement...
      </div>
    );
  }

  if (!utilisateur) {
    return (
      <Navigate to="/connexion" replace state={{ de: emplacement.pathname }} />
    );
  }
  return <Outlet />;
}
