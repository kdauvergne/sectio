import type { Poteau } from "@/types/api";
import { libelleSection } from "@/lib/poteaux";
import { TableCell, TableRow } from "@/components/ui/table";

type LignePoteauProps = {
  poteau: Poteau;
};

export function LignePoteau({ poteau }: LignePoteauProps) {
  return (
    <TableRow>
      <TableCell className="font-medium">{poteau.repere}</TableCell>
      <TableCell>{libelleSection(poteau)}</TableCell>
      <TableCell className="text-right">
        {poteau.L0.toFixed(2).replace(".", ",")}
      </TableCell>
      <TableCell className="text-right">{poteau.G}</TableCell>
      <TableCell className="text-right">{poteau.Q}</TableCell>
    </TableRow>
  );
}
