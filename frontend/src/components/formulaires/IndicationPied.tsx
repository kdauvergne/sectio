type Props = {
  erreurEnvoi?: string;
  nbErreurs: number;
};

export function IndicationPied({ erreurEnvoi, nbErreurs }: Props) {
  if (erreurEnvoi) {
    return <p className="info-carte text-destructive">{erreurEnvoi}</p>;
  }
  if (nbErreurs > 0) {
    return (
      <p className="info-carte text-destructive">
        {nbErreurs} {nbErreurs > 1 ? "champs" : "champ"} à corriger
      </p>
    );
  }
  return (
    <p className="hidden info-carte text-muted-foreground sm:block">
      Entrée pour créer · Échap pour annuler
    </p>
  );
}
