% BAKASHOV (2147174)
% MADZOU (2117902)

include "globals.mzn";

%-----------------------------------------------------------------------------%
% Variables de décisions
%-----------------------------------------------------------------------------%

% Nombre devant satisfaire les critères
var 1000..9999: nombre;

% Décomposition du nombre en un ensemble de chiffres
array[1..4] of var 1..9: chiffres;

%-----------------------------------------------------------------------------%
% Objectif
%-----------------------------------------------------------------------------%

% Variable à minimiser
var int: p;

%-----------------------------------------------------------------------------%
% Partie étudiant
%-----------------------------------------------------------------------------%
constraint nombre = 1000 * chiffres[1] + 100 * chiffres[2] + 10 * chiffres[3] + chiffres[4];

% 1 : C'est un nombre pair
constraint chiffres[4] mod 2 = 0;

% 2 : Le chiffre 0 n’est pas présent dans le nombre. Déjà précisé dans la déclaration de chiffres

% 3 : Les 4 chiffres sont différents.
constraint alldifferent(chiffres);

% 4 : Le chiffre à la position des milliers est supérieur à celui à la position des centaines.
constraint chiffres[1] > chiffres[2];

% 5 : Le chiffre à la position des dizaines est inférieur à celui à la position des unités.
constraint chiffres[3] < chiffres[4];

% 6 : Le chiffre à la position des centaines est supérieur à celui à la position des unités.
constraint chiffres[2] > chiffres[4];

% 7 : La somme des 4 chiffres est supérieure à 15.
constraint sum(chiffres) > 15;

% 8 : Le produit des 3 derniers chiffres (chiffre à la position des centaines×chiffre à la position des dizaines
%× chiffre à la position des unités) doit être minimisé.
constraint p = chiffres[2] * chiffres[3] * chiffres[4];
solve minimize p;

%-----------------------------------------------------------------------------%

output [
  "Nombre: ", show(nombre), "\n",
  "Produit des trois derniers chiffres: ", show(p), "\n",
  show(nombre)
];

