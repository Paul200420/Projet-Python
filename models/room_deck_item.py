from dataclasses import dataclass
# Assurez-vous que l'import de Room fonctionne
from models.room import Room 

@dataclass
class RoomDeckItem:
    """
    Encapsule une Room pour suivre son état dans la pioche (si elle est disponible ou déjà placée).
    Ceci est essentiel pour implémenter la règle "Quand une pièce est ajoutée au manoir,
    elle est retirée de la pioche et ne peut plus être tirée."
    """
    
    # L'instance de la pièce elle-même (le modèle Room)
    room: Room
    
    # L'état : True si elle n'a pas encore été placée dans le manoir.
    is_in_deck: bool = True
