# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Installe les extensions listées dans .vscode/extensions.json si elles manquent."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def load_recommendations(path: Path) -> list[str]:
    """Lit extensions.json (JSONC) en retirant les commentaires // hors chaînes."""
    raw = path.read_text(encoding="utf-8-sig")
    raw = re.sub(r'(?m)^\s*//.*$', "", raw)  # commentaires pleine ligne
    raw = re.sub(r',(\s*[}\]])', r"\1", raw)  # virgules finales
    return json.loads(raw)["recommendations"]


def main() -> int:
    # Sous Windows, "code" seul peut désigner un script shell non exécutable : préférer code.cmd.
    code = shutil.which("code.cmd") or shutil.which("code")
    if code is None:
        print("CLI 'code' introuvable dans le PATH, installation ignorée.")
        return 0

    try:
        wanted = load_recommendations(Path(__file__).parent / "extensions.json")
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"Impossible de lire extensions.json : {exc}")
        return 1

    result = subprocess.run(
        [code, "--list-extensions"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    installed = {line.strip().lower() for line in result.stdout.splitlines()}

    missing = [ext for ext in wanted if ext.lower() not in installed]
    if not missing:
        print("Toutes les extensions sont déjà installées.")
        return 0

    failed = []
    for ext in missing:
        print(f"Installation de {ext}...")
        proc = subprocess.run([code, "--install-extension", ext], check=False)
        if proc.returncode != 0:
            failed.append(ext)

    if failed:
        print(f"Échec pour : {', '.join(failed)}")
        return 1

    print("Terminé. Recharge la fenêtre si certaines extensions ne sont pas actives.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
