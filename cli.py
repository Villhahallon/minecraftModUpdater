from pathlib import Path
import argparse

from core.config import Config
from core.updater import run_updater

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--mc", default="1.21.1")
    parser.add_argument("--loader", default="fabric")
    parser.add_argument("--mods", default="mods.txt")
    parser.add_argument("--out", default="mods")

    args = parser.parse_args()

    config = Config(
        minecraft_version=args.mc,
        loader=args.loader,
        base_dir=Path(args.out),
        mods_file=Path(args.mods),
    )

    results = run_updater(config)

    print(f"\nProfile: {args.mc} / {args.loader}")
    print("=" * 40)

    for line in results:
        print(line)

if __name__ == "__main__":
    main()