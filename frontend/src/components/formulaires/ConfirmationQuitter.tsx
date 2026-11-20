import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

type Props = {
  ouvert: boolean;
  onOuvertChange: (ouvert: boolean) => void;
  onQuitter: () => void;
  consequence: string;
};

export function ConfirmationQuitter({
  ouvert,
  onOuvertChange,
  onQuitter,
  consequence,
}: Props) {
  return (
    <AlertDialog open={ouvert} onOpenChange={onOuvertChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Quitter le formulaire ?</AlertDialogTitle>
          <AlertDialogDescription>
            {consequence} et les informations saisies seront perdues.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Continuer la saisie</AlertDialogCancel>
          <AlertDialogAction onClick={onQuitter}>Quitter</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
