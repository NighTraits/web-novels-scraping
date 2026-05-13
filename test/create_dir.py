from pathlib import Path

# print(Path.cwd())
Path(f"{Path.cwd()}/my/directory").mkdir(parents=True, exist_ok=True)
