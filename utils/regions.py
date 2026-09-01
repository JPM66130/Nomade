def region_de(ville: str) -> str:
    """
    Retourne une région fictive selon la ville.
    À personnaliser selon tes besoins.
    """
    ville = ville.lower()

    if "perpignan" in ville or "ille-sur-tet" in ville:
        return "Occitanie"
    if "lyon" in ville:
        return "Auvergne-Rhône-Alpes"
    if "marseille" in ville:
        return "Provence-Alpes-Côte d'Azur"

    return "Région inconnue"
