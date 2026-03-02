from pathlib import Path
import requests

from core.modrinth import get_versions
from core.state import load_state, save_state
from core.config import Config


def read_mods(mods_file: Path) -> list[str]:
    return [
        line.strip()
        for line in mods_file.read_text().splitlines()
        if line.strip()
    ]


def download_file(url: str, path: Path) -> None:
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def update_mod(slug: str, config: Config, state: dict) -> str:
    versions = get_versions(
        slug,
        config.minecraft_version,
        config.loader
    )

    if not versions:
        return f"{slug}: no compatible versions"
    
    latest = versions[0]
    latest_version = latest["version_number"]
    file_info = latest["files"][0]

    installed_version = state.get(slug)

    if installed_version == latest_version:
        return f"{slug}: up to date ({latest_version})"
    
    config.mods_dir.mkdir(parents=True, exist_ok=True)

    #remove old files
    for file in config.mods_dir.glob(f"{slug}.jar"):
        file.unlink(missing_ok=True)

    download_file(
        file_info["url"],
        config.mods_dir / file_info["filename"]
    )

    state[slug] = latest_version

    if installed_version:
        return f"{slug}: updated {installed_version} → {latest_version}"
    else:
        return f"{slug}: installed {latest_version}"
    
def run_updater(config: Config) -> list[str]:
    mods = read_mods(config.mods_file)
    state = load_state(config.state_file)

    results = []

    for slug in mods:
        try:
            result = update_mod(slug, config, state)
        except Exception as e:
            result = f"{slug}: error ({e})"

        results.append(result)

    save_state(config.state_file, state)
    return results