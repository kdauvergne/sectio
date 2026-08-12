import { useState } from "react";
import { Link } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import {
  Building2,
  ChevronsUpDown,
  FolderKanban,
  LayoutDashboard,
  LogOut,
  Settings,
  UserCircle,
} from "lucide-react";

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

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useIsMobile } from "@/hooks/use-mobile";

type LienNavigation = {
  titre: string;
  url: string;
  icone: LucideIcon;
};

type Utilisateur = {
  nom: string;
  prenom: string;
  titre: string;
  avatar: string;
};

const NAVIGATION: LienNavigation[] = [
  {
    titre: "Tableau de bord",
    url: "/",
    icone: LayoutDashboard,
  },
  {
    titre: "Projets",
    url: "/projets",
    icone: FolderKanban,
  },
];

const user: Utilisateur = {
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
              <Link to="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Building2 className="size-4" />
                </div>

                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-bold">Sectio</span>
                </div>
              </Link>
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
                const Icone = lien.icone;

                return (
                  <SidebarMenuItem key={lien.url}>
                    {estProjets ? (
                      <SidebarMenuButton
                        tooltip={lien.titre}
                        onClick={() => setProjetsOuvert((ouvert) => !ouvert)}
                      >
                        <Icone />
                        <span>{lien.titre}</span>
                      </SidebarMenuButton>
                    ) : (
                      <SidebarMenuButton asChild tooltip={lien.titre}>
                        <Link to={lien.url}>
                          <Icone />
                          <span>{lien.titre}</span>
                        </Link>
                      </SidebarMenuButton>
                    )}

                    {estProjets && projetsOuvert && (
                      <SidebarMenuSub>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton asChild>
                            <Link to="/projets/alpha">Projet Alpha</Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton asChild>
                            <Link to="/projets/beta">Projet Beta</Link>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>

                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton asChild>
                            <Link to="/projets/gamma">Projet Gamma</Link>
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

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton
                  className="data-popup-open:bg-sidebar-accent data-popup-open:text-sidebar-accent-foreground"
                  size="lg"
                >
                  <Avatar className="h-8 w-8 rounded-lg">
                    <AvatarImage
                      src={user.avatar}
                      alt={`${user.prenom} ${user.nom}`}
                    />
                    <AvatarFallback>PD</AvatarFallback>
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
                  <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                    <Avatar className="h-8 w-8 rounded-lg">
                      <AvatarImage
                        src={user.avatar}
                        alt={`${user.prenom} ${user.nom}`}
                      />
                      <AvatarFallback className="rounded-lg">PD</AvatarFallback>
                    </Avatar>

                    <div className="grid flex-1 text-left text-sm leading-tight">
                      <span className="truncate font-medium">
                        {user.prenom} {user.nom}
                      </span>

                      <span className="truncate text-xs">{user.titre}</span>
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
