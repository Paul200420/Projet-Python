-----SECTION 1 – INSTALLATION ET LANCEMENT DU JEU-----

Prérequis :
-Python 3.10 ou supérieur
-Le module Pygame doit être installé

Installation :
Dans un terminal, exécuter : pip install pygame
Lancement de la version graphique :
-Exécuter le fichier : main_graphiqc.py. Une fenêtre de jeu apparaît automatiquement.

-----SECTION 2 – FONCTIONNEMENT DU MANOIR-----

Le manoir est généré pièce par pièce selon vos déplacements.
Quand vous tentez d’aller dans une direction vide :
-Trois salles sont tirées selon leur rareté et vos bonus.
-Vous en choisissez une en payant son coût en gemmes(ou pas).

La salle est alors construite définitivement.

Certaines salles ont des effets immédiats, d’autres modifient les tirages de salles futures, et d’autres donnent du loot une seule fois.

-----SECTION 3 – COMMANDES DU JOUEUR-----

Déplacements :
-Haut : Flèche haut ou Z
-Bas : Flèche bas ou S
-Gauche : Flèche gauche ou Q
-Droite : Flèche droite ou D
-Chaque déplacement coûte 1 pas, sauf si la salle le rembourse.

Tirage de nouvelles salles :
Lorsqu’une direction mène à une zone vide, trois salles sont proposées.
-Pour ouvrir la  proposition des tirages : Barre espace
Pour les choisir :
-On choisit la salle à l'aide des fleches gauche droite du clavier.
-Confirmer le choix : Touche 0
Relancer un tirage si vous avez un dé : Touche R

Interaction :
-Ramasser un objet ou interagir : Touche F
-Acheter dans un magasin (Kitchen) : touches 1 à 5 selon l’article souhaité

Objectif :
-Atteindre la salle finale appelée Antechamber.
-Vous perdez lorsque vous n’avez plus de pas.

-----SECTION 4 – LISTE TEXTUELLE DES SALLES ET EFFETS-----

Ci-dessous se trouvent toutes les salles présentes dans le jeu.

Salle : Entrance Hall
Coût : 0 gemme
Effet : Point de départ. Aucun effet particulier.

Salle : Plain Room (Sauna)
Coût : 0 gemme
Effet : Donne 2 Small Business une seule fois.

Salle : Locker Room
Coût : 1 gemme
Effet : Le déplacement vers cette salle ne coûte aucun pas (rembourse 1 pas). Peut contenir un casier.

Salle : Kitchen
Coût : 0 gemme
Effet : 30 pour cent de chance d’accorder +2 pas (une seule fois). Contient un comptoir pour acheter des objets (touches 1 à 5).

Salle : Pantry
Coût : 2 gemmes
Effet : +3 pas et +1 clé, une seule fois.

Salle : Garden
Coût : 1 gemme
Effet : Donne +1 gemme (garanti), puis 30 pour cent d’obtenir +1 gemme supplémentaire. Une seule fois.
Condition de placement : uniquement en bordure du manoir.

Salle : Utility Room (appelée Treasure Room dans le code)
Coût : 3 gemmes
Effet : +8 or, +15 clés, une seule fois. Peut contenir un coffre et un objet permanent.
Condition de placement : ne peut pas apparaître sur la rangée de départ (r < 4).

Salle : Armory
Coût : 1 gemme
Effet : Donne 1 clé (garanti) et 50 pour cent d’obtenir un objet permanent dans la salle. Une seule fois.

Salle : Library
Coût : 2 gemmes
Effet : Donne +3 dés, une seule fois.

Salle : Furnace
Coût : 0 gemme
Effet : À chaque entrée : perte de 2 pas. La première fois : +10 or, +5 clés, +7 gemmes.
Influence sur les tirages : augmente la fréquence des salles riches (TreasureRoom, Armory).

Salle : Greenhouse
Coût : 1 gemme
Effet : Donne 2 Small Business une seule fois.
Influence sur les tirages : favorise Garden et Pantry.

Salle : Solarium
Coût : 1 gemme
Effet : Donne 1 clé, une seule fois.
Influence sur les tirages : favorise Library et Plain Room.

Salle : Veranda
Coût : 0 gemme
Effet : 30 pour cent de chance de gagner une gemme. Augmente les chances de trouver de la nourriture dans les prochaines salles.
Influence sur les tirages : favorise Garden.

Salle : Maid’s Chamber
Coût : 0 gemme
Effet : 20 pour cent de chance de gagner un dé, une seule fois.

Salle : Master Bedroom
Coût : 1 gemme
Effet : Donne 1 clé à son apparition dans un tirage (bonus au moment du choix).

Salle : Weight Room
Coût : 0 gemme
Effet : Au tirage : vous perdez la moitié de vos pas actuels (une seule fois).

Salle : Chamber of Mirrors
Coût : 0 gemme
Effet : Débloque la salle Rumpus Room pour les futurs tirages (une seule fois).

Salle : Rumpus Room 
Coût : 1 gemme
Effet : Donne +8 or une seule fois.
Uniquement disponible après avoir visité Chamber of Mirrors.

Salle : Antechamber
Coût : 0 gemme
Effet : Salle finale. Atteindre cette salle signifie victoire.

-----SECTION 5 – CONDITIONS DE VICTOIRE ET DE DÉFAITE-----

Vous gagnez :
-Lorsque vous atteignez la salle Antechamber.

Vous perdez :
-Lorsque vos pas tombent à zéro.

BON JEU !




