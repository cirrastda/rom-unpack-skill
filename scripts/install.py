#!/usr/bin/env python3
"""Instala/atualiza/remove as skills rom-unpack nos editores de IA suportados.

Uso:
  install.py install   <editor|all> [--home DIR]
  install.py uninstall <editor|all> [--home DIR]
  install.py list

Editores: claude, vscode, cursor, codex, antigravity.
Fonte única: skills/skills.json + skills/_shared/*.md (renderizados por editor).
Cada execução sobrescreve os arquivos (idempotente), então serve também como update.
"""
import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "skills" / "_shared"
MANIFEST = ROOT / "skills" / "skills.json"
TOOL_SRC = ROOT / "tools" / "rom_identify.py"

ARGS_PLACEHOLDER = {
    "claude": "`$ARGUMENTS`",
    "codex": "`$ARGUMENTS`",
}
ARGS_DEFAULT = "o texto digitado pelo usuário após o comando (vazio = sem argumentos)"
EDITORS = ("claude", "vscode", "cursor", "codex", "antigravity")


def vscode_user_dirs(home: Path):
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    elif system == "Darwin":
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    dirs = [base / "Code" / "User" / "prompts"]
    insiders = base / "Code - Insiders" / "User"
    if insiders.exists():
        dirs.append(insiders / "prompts")
    return dirs


def target_dirs(editor: str, home: Path):
    if editor == "claude":
        return [home / ".claude" / "commands"]
    if editor == "cursor":
        return [home / ".cursor" / "commands"]
    if editor == "codex":
        return [Path(os.environ.get("CODEX_HOME", home / ".codex")) / "prompts"]
    if editor == "antigravity":
        return [home / ".gemini" / "antigravity" / "global_workflows"]
    if editor == "vscode":
        return vscode_user_dirs(home)
    raise ValueError(editor)


def filename(editor: str, name: str) -> str:
    return f"{name}.prompt.md" if editor == "vscode" else f"{name}.md"


def read_shared(name: str) -> str:
    return (SHARED / name).read_text(encoding="utf-8").strip()


def render(editor: str, skill: dict) -> str:
    args = ARGS_PLACEHOLDER.get(editor, ARGS_DEFAULT)
    phases = skill["phases"]
    parts = [f"# /{skill['name']} — {skill['title']}", ""]
    if len(phases) > 1:
        parts.append(
            "Execute as fases abaixo **em ordem** (" + " → ".join(p.upper() for p in phases) +
            "). Se uma fase falhar ou exigir resposta do usuário, pare e resolva antes de seguir."
        )
    else:
        parts.append(f"Execute somente a fase **{phases[0].upper()}** descrita abaixo.")
    parts += ["", read_shared("common.md").replace("{{ARGS}}", args)]
    for p in phases:
        parts += ["", read_shared(f"phase-{p}.md")]
    body = "\n".join(parts) + "\n"

    desc = skill["description"].replace('"', "'")
    hint = skill["argument_hint"].replace('"', "'")
    if editor == "claude":
        fm = f'---\ndescription: "{desc}"\nargument-hint: "{hint}"\n---\n\n'
    elif editor == "codex":
        fm = f'---\ndescription: "{desc}"\nargument-hint: "{hint}"\n---\n\n'
    elif editor == "vscode":
        fm = f'---\nagent: agent\ndescription: "{desc}"\nargument-hint: "{hint}"\n---\n\n'
    elif editor == "antigravity":
        fm = f'---\ndescription: "{desc}"\n---\n\n'
    else:  # cursor commands são markdown puro
        fm = ""
    return fm + body


def install_tool(home: Path):
    dest = home / ".rom-unpack"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TOOL_SRC, dest / "rom_identify.py")
    return dest / "rom_identify.py"


def do_install(editor: str, home: Path, skills):
    for d in target_dirs(editor, home):
        d.mkdir(parents=True, exist_ok=True)
        for s in skills:
            out = d / filename(editor, s["name"])
            out.write_text(render(editor, s), encoding="utf-8", newline="\n")
        print(f"  + {editor}: {len(skills)} skills em {d}")


def do_uninstall(editor: str, home: Path, skills):
    for d in target_dirs(editor, home):
        n = 0
        for s in skills:
            f = d / filename(editor, s["name"])
            if f.exists():
                f.unlink()
                n += 1
        print(f"  - {editor}: {n} skills removidas de {d}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("install", "uninstall", "list"))
    ap.add_argument("editor", nargs="?", default="all", choices=EDITORS + ("all",))
    ap.add_argument("--home", help="diretório home alternativo (testes)")
    a = ap.parse_args()

    skills = json.loads(MANIFEST.read_text(encoding="utf-8"))["skills"]
    if a.action == "list":
        for s in skills:
            print(f"/{s['name']:<26} {s['description']}")
        return 0

    home = Path(a.home) if a.home else Path.home()
    editors = EDITORS if a.editor == "all" else (a.editor,)
    if a.action == "install":
        for e in editors:
            do_install(e, home, skills)
        print(f"  + ferramenta: {install_tool(home)}")
    else:
        for e in editors:
            do_uninstall(e, home, skills)
        tool_dir = home / ".rom-unpack"
        if a.editor == "all" and tool_dir.exists():
            shutil.rmtree(tool_dir)
            print(f"  - ferramenta removida: {tool_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
