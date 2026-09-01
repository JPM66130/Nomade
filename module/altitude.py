import requests

def get_altitude_profile(coords):
    """
    Reçoit une liste de points [lon, lat]
    Retourne un dictionnaire avec :
    - altitudes
    - alt_min, alt_max, denivele, pente_moyenne
    """
    url = "https://api.open-elevation.com/api/v1/lookup"
    points = [{"latitude": lat, "longitude": lon} for lon, lat in coords]
    response = requests.post(url, json={"locations": points})
    results = response.json()["results"]

    altitudes = [r["elevation"] for r in results]
    alt_min = min(altitudes)
    alt_max = max(altitudes)
    denivele = alt_max - alt_min
    pente_moyenne = denivele / len(altitudes)

    return {
        "altitudes": altitudes,
        "alt_min": alt_min,
        "alt_max": alt_max,
        "denivele": denivele,
        "pente_moyenne": pente_moyenne
    }
