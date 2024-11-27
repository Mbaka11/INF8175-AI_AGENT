% BAKASHOV (2147174)
% MADZOU (2117902)

include "globals.mzn";

%-----------------------------------------------------------------------------%
% Données
%-----------------------------------------------------------------------------%

% Nombre d'acteurs et de rôles
int: n;
% Couleurs des costumes
enum costumes; 
% Costume démandé pour un rôle i (première dimension) par un acteur j (seconde dimension)
array[1..n,1..n] of costumes: choix_costume;

%-----------------------------------------------------------------------------%
% Variables de décisions
%-----------------------------------------------------------------------------%

% Variables de décision pour assigner un acteur à un rôle
array [1..n] of var 1..n: assignation_role;

%-----------------------------------------------------------------------------%
% Partie étudiant
%-----------------------------------------------------------------------------%
% 1 : Chaque acteur doit avoir un rôle unique
constraint all_different(assignation_role);

% 2 : Non-adjacence des rôles pour les acteurs voisins
constraint forall(i in 1..n-1) (
    abs(assignation_role[i] - assignation_role[i+1]) > 1
);

% 3 : Chaque costume n'est utilisé que par un seul acteur / une seule fois
constraint
  forall(i in 1..n, j in 1..n where i != j) (
    choix_costume[assignation_role[i], i] != choix_costume[assignation_role[j], j]
  );
%-----------------------------------------------------------------------------%

output	
  ["L'acteur " ++ format(i) ++ 
   " prendra le rôle " ++ format(fix(assignation_role[i])) ++ 
   " (costume " ++ format(choix_costume[fix(assignation_role[i]), i]) ++ ")" ++"\n" 
  | i in 1..n];