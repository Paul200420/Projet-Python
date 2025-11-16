from enum import Enum

class CouleurPiece(Enum):
    JAUNE = 1     # magasins (on pet acheter des items en entrant dans la salle)
    VERTE = 2     # jardins et probabilite varié d'obtenir des objets
    VIOLETTE = 3  # (gain d'objets ou d'items quand on rentre deadans)
    ROUGE = 5     # dangereuses (un malus quand on rentre dedans)
    BLEUE = 6     # communes (sans effets speciales)
