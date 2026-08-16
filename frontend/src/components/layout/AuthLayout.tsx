import { Outlet } from "react-router-dom";
import { Square } from "lucide-react";

export function AuthLayout() {
  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="bg-secondary text-secondary-foreground hidden flex-col justify-between p-10 lg:flex">
        <div className="flex items-center gap-2 text-lg font-medium">
          <Square className="size-5" />
          <strong>Sectio</strong>
        </div>

        <blockquote className="space-y-3">
          <p className="text-4xl leading-snug font-bold">
            Le dimensionnement n'a jamais été aussi facile.
          </p>
          <footer className="text-sm opacity-70">
            Dimensionnement de poteaux en béton armé - Eurocode 2
          </footer>
        </blockquote>
      </div>
      <div className="flex items-center justify-center p-6 lg:p-10">
        {/* ROUTES */}
        <Outlet />
      </div>
    </div>
  );
}
