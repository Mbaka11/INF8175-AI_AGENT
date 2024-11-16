% BAKASHOV (2147174)
% MADZOU (2117902)

include "globals.mzn"; 

%-----------------------------------------------------------------------------%
% Données
%-----------------------------------------------------------------------------%

% Nombre de tâches
int: n;
% Durée maximal du projet
int: m;
% Limite de ressources pouvant être partagées entre les tâches en cours
int: limite;

% Durée des tâches
array[1..n] of 1..m: duree_tache;
% Ressources requises par les tâches
array[1..n] of 1..m: ressource_tache;

%-----------------------------------------------------------------------------%
% Variables de décisions
%-----------------------------------------------------------------------------%

array[1..n] of var 1..m: debut_tache; % Début des tâches
array[1..n] of var 1..m: fin_tache; % Fin des tâches

%-----------------------------------------------------------------------------%
% Objectif
%-----------------------------------------------------------------------------%

% Fin du projet
var int: fin_projet;

%-----------------------------------------------------------------------------%
% Partie étudiant
%-----------------------------------------------------------------------------%
% 1. Chaque tâche doit se terminer après sa durée
constraint forall(i in 1..n) (
    fin_tache[i] = debut_tache[i] + duree_tache[i]
);

% 2. Définition de la fin du projet comme la fin de la dernière tâche terminée
constraint fin_projet = max(i in 1..n)(fin_tache[i]);

% 3. Limite de ressources simultanées : contrainte cumulative
constraint cumulative(debut_tache, duree_tache, ressource_tache, limite);

% 4. Limiter le nombre de démarrages simultanés à chaque instant t
constraint forall(t in 1..m) (
    sum([bool2int(debut_tache[i] = t) | i in 1..n]) <= 2
);

solve minimize fin_projet;
%-----------------------------------------------------------------------------%

output [
  "Envergure du projet  : ", show(fin_projet), "\n",
  "Début des tâches     : ", show(debut_tache), "\n",
  "Fin des tâches       : ", show(fin_tache), "\n",
];