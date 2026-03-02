import requests

HEADERS = {
    "User-Agent": "MinecraftModUpdater/1.0"
}

def get_versions(slug: str, mc_version: str, loader: str) -> list(dict):
    """
    Fetch compatible versions for a mod
    """
    url = f"https://api.modrinth.com/v2/project/{slug}/version"

    params = {
        "game_versions": f'["{mc_version}"]',
        "loaders": f'["{loader}"]'
    }

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()