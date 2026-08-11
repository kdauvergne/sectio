import type { Poteau } from "@/types/api";
import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { LignePoteau } from "./LignePoteau";

type TableauPoteauxProps = {
  poteaux: Poteau[];
};

export function TableauPoteaux({ poteaux }: TableauPoteauxProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="font-bold">Repère</TableHead>
          <TableHead className="font-bold">Section</TableHead>
          <TableHead className="font-bold text-right">L0 (m)</TableHead>
          <TableHead className="font-bold text-right">G (kN)</TableHead>
          <TableHead className="font-bold text-right">Q (kN)</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {poteaux.map((poteau) => (
          <LignePoteau key={poteau.id} poteau={poteau} />
        ))}
      </TableBody>
    </Table>
  );
}
