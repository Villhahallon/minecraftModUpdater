from pathlib import Path

class Config:
    def __init__(
        self,
        minecraft_version: str,
        loader: str,
        base_dir: Path,
        mods_file: Path,
    ):

        self.minecraft_version = minecraft_version
        self.loader = loader
        self.base_dir = base_dir
        self. mods_file = mods_file

    @property
    def profile_dir(self) -> Path:
        return self.base_dir / self.minecraft_version / self.loader
    
    @property
    def mods_dir(self) -> Path:
        return self.profile_dir / "mods"
    
    @property
    def state_file(self) -> Path:
        return self.profile_dir / "mods_state.json"
