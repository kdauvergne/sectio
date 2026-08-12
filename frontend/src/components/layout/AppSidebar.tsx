import { useState } from "react";

import {
  LayoutDashboard,
  FolderKanban,
  Building2,
  ChevronsUpDown,
  LogOut,
  Settings,
  UserCircle,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { useIsMobile } from "@/hooks/use-mobile";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

type LienNavigation = {
  titre: string;
  url: string;
  icone: LucideIcon;
};

type Utilisateurs = {
  nom: string;
  prenom: string;
  titre: string;
  avatar: string;
};

const NAVIGATION: LienNavigation[] = [
  { titre: "Tableau de bord", url: "/", icone: LayoutDashboard },
  { titre: "Projets", url: "/projets", icone: FolderKanban },
];

const user: Utilisateurs = {
  nom: "Dubois",
  prenom: "Philippe",
  titre: "Ingénieur structure",
  avatar: "https://github.com/shadcn.png",
};

export function AppSidebar() {
  const isMobile = useIsMobile();

  const [projetsOuvert, setProjetsOuvert] = useState(false);

  return (
    <Sidebar collapsible="icon" variant="inset">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Building2 className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-bold">Sectio</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <div className="mx-2 h-px bg-sidebar-border" />
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {NAVIGATION.map((lien) => {
                const estProjets = lien.titre === "Projets";

                return (
                  <SidebarMenuItem key={lien.url}>
                    {estProjets ? (
                      // Pas de asChild ici : SidebarMenuButton reste un <button> natif,
                      // donc pas de href, pas de navigation → seul le toggle s'exécute.
                      <SidebarMenuButton
                        tooltip={lien.titre}
                        onClick={() => setProjetsOuvert((ouvert) => !ouvert)}
                      >
                        <lien.icone />
                        <span>{lien.titre}</span>
                      </SidebarMenuButton>
                    ) : (
                      <SidebarMenuButton asChild tooltip={lien.titre}>
                        <a href={lien.url}>
                          <lien.icone />
                          <span>{lien.titre}</span>
                        </a>
                      </SidebarMenuButton>
                    )}

                    {estProjets && projetsOuvert && (
                      <SidebarMenuSub>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton isActive={false}>
                            Projet Alpha
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton isActive={false}>
                            Projet Beta
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton isActive={false}>
                            Projet Gamma
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </SidebarMenuSub>
                    )}
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      {/* Bloc footer Sidebar utilisateur */}
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton
                  className="data-popup-open:bg-sidebar-accent data-popup-open:text-sidebar-accent-foreground md:h-8 md:p-0"
                  size="lg"
                >
                  <Avatar className="h-8 w-8 rounded-lg">
                    <AvatarImage
                      src="https://github.com/shadcn.png"
                      alt="@shadcn"
                    />
                    <AvatarFallback>DP</AvatarFallback>
                  </Avatar>
                  <div className="grid flex-1 text-left text-sm leading-tight">
                    <span className="truncate font-medium">
                      {user.prenom} {user.nom}
                    </span>
                    <span className="truncate text-xs">{user.titre}</span>
                  </div>
                  <ChevronsUpDown className="ml-auto size-4" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="w-(--anchor-width) min-w-45 rounded-lg p-2"
                side={isMobile ? "bottom" : "top"}
                sideOffset={8}
              >
                <DropdownMenuLabel className="font-normal">
                  <div className="flex items-left gap-2 px-1 py-1.5 text-left text-sm">
                    <Avatar className="h-8 w-8 rounded-lg">
                      <AvatarImage src={user.avatar} />
                      <AvatarFallback className="rounded-lg">CN</AvatarFallback>
                    </Avatar>
                    <div className="grid flex-1 text-left text-sm leading-tight">
                      <span className="truncate font-medium">
                        {user.nom} {user.prenom}
                      </span>
                      <span className="truncate text-xs">{user.titre} </span>
                    </div>
                  </div>
                </DropdownMenuLabel>

                <DropdownMenuGroup>
                  <DropdownMenuItem>
                    <UserCircle />
                    Compte
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings />
                    Paramètres
                  </DropdownMenuItem>
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuItem variant="destructive">
                  <LogOut />
                  Se déconnecter
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
