import { Fragment } from "react";
import { Link } from "react-router-dom";

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

export type ElementFilAriane = {
  libelle: string;
  url?: string;
};

export function FilAriane({ elements }: { elements: ElementFilAriane[] }) {
  return (
    <Breadcrumb className="mb-4">
      <BreadcrumbList>
        {elements.map((element, index) => {
          const estDernier = index === elements.length - 1;

          return (
            <Fragment key={`${index}-${element.libelle}`}>
              {index > 0 && <BreadcrumbSeparator />}
              <BreadcrumbItem>
                {estDernier ? (
                  <BreadcrumbPage>{element.libelle}</BreadcrumbPage>
                ) : element.url ? (
                  <BreadcrumbLink asChild>
                    <Link to={element.url}>{element.libelle}</Link>
                  </BreadcrumbLink>
                ) : (
                  element.libelle
                )}
              </BreadcrumbItem>
            </Fragment>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
