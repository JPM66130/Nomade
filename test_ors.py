from utils.geo import _ors_client


def main():
	client = _ors_client()
	if client is None:
		raise RuntimeError("Clé OpenRouteService indisponible")

	coords = [[2.621, 42.668], [2.395, 42.55]]
	route = client.directions(coords, profile="driving-car", format="geojson")
	print(route["features"][0]["properties"]["summary"])


if __name__ == "__main__":
	main()
