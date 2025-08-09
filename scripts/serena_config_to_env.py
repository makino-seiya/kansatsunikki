#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def load_simple_yaml(path: Path) -> dict:
    config = {}
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        # strip single or double quotes if wrapped
        if (value.startswith("'") and value.endswith("'")) or (
            value.startswith('"') and value.endswith('"')
        ):
            value = value[1:-1]
        config[key] = value
    return config


def main() -> int:
    config_env_path = os.environ.get("SERENA_CONFIG")
    if config_env_path:
        config_path = Path(os.path.expanduser(config_env_path))
    else:
        # Prefer project-local .serena/config.yml, fallback to XDG path
        local_path = Path.cwd() / ".serena" / "config.yml"
        if local_path.exists():
            config_path = local_path
        else:
            config_path = Path(os.path.expanduser("~/.config/serena/config.yml"))

    try:
        data = load_simple_yaml(config_path)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        print("Hint: create .serena/config.yml in the project or set SERENA_CONFIG, or place ~/.config/serena/config.yml.", file=sys.stderr)
        return 1

    # target env file at repo root
    repo_root = Path.cwd()
    env_file = repo_root / ".serena.env"

    lines = []
    for k, v in data.items():
        lines.append(f"{k}={v}")

    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {env_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())