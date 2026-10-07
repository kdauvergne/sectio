import { useState } from "react";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Outlet } from "react-router-dom";
import { AppSidebar } from "./AppSidebar";
import { FilAriane, type ElementFilAriane } from "./FilAriane";

export function AppLayout() {
  const [filAriane, setFilAriane] = useState<ElementFilAriane[]>([]);

  return (
    <SidebarProvider>
      <AppSidebar />

      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center gap-2 px-4">
          <SidebarTrigger />
          {filAriane.length > 0 && (
            <>
              <Separator
                orientation="vertical"
                className="mr-2 data-vertical:h-4 data-vertical:self-center"
              />
              <FilAriane elements={filAriane} />
            </>
          )}
        </header>

        <div className="px-10 pb-6">
          <Outlet context={{ setFilAriane }} />
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
