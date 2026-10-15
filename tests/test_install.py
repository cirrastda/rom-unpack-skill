import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL = ROOT / "scripts" / "install.py"
IDENT = ROOT / "tools" / "rom_identify.py"
NAMES = [s["name"] for s in json.loads((ROOT / "skills" / "skills.json").read_text(encoding="utf-8"))["skills"]]


def run(*args, env=None):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, env=env)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.env = {**os.environ, "APPDATA": str(self.home / "AppData"), "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "CODEX_HOME": str(self.home / ".codex")}

    def tearDown(self):
        self.tmp.cleanup()

    def test_all_editors(self):
        r = run(INSTALL, "install", "all", "--home", self.home, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        for n in NAMES:
            self.assertTrue((self.home / ".claude/commands" / f"{n}.md").is_file())
            self.assertTrue((self.home / ".cursor/commands" / f"{n}.md").is_file())
            self.assertTrue((self.home / ".codex/prompts" / f"{n}.md").is_file())
            self.assertTrue((self.home / ".gemini/antigravity/global_workflows" / f"{n}.md").is_file())
        self.assertTrue((self.home / ".rom-unpack/rom_identify.py").is_file())
        text = (self.home / ".claude/commands/fix-rom-and-build.md").read_text(encoding="utf-8")
        self.assertIn("$ARGUMENTS", text)
        self.assertIn("Fase FIX", text)
        self.assertNotIn("{{", text)

    def test_composite_has_all_phases_in_order(self):
        run(INSTALL, "install", "claude", "--home", self.home, env=self.env)
        t = (self.home / ".claude/commands/read-and-build-rom.md").read_text(encoding="utf-8")
        i = [t.index(f"Fase {p}") for p in ("READ", "DECOMPILE", "BUILD")]
        self.assertEqual(i, sorted(i))

    def test_uninstall(self):
        run(INSTALL, "install", "all", "--home", self.home, env=self.env)
        r = run(INSTALL, "uninstall", "all", "--home", self.home, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.home / ".claude/commands/read-rom.md").exists())
        self.assertFalse((self.home / ".rom-unpack").exists())


class IdentifyTests(unittest.TestCase):
    def ident(self, data, name):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / name
            p.write_bytes(data)
            r = run(IDENT, p)
            self.assertEqual(r.returncode, 0, r.stderr)
            return json.loads(r.stdout)

    def test_nes(self):
        info = self.ident(b"NES\x1a\x02\x01\x01\x00" + bytes(16 + 32768 + 8192 - 8), "a.nes")
        self.assertEqual(info["best_guess"], "NES")
        self.assertTrue(info["identified"])

    def test_gb(self):
        d = bytearray(32768)
        d[0x104:0x108] = b"\xCE\xED\x66\x66"
        self.assertEqual(self.ident(bytes(d), "a.gb")["best_guess"], "Game Boy")

    def test_ambiguous_bin_not_identified(self):
        info = self.ident(bytes(100), "a.bin")
        self.assertFalse(info["identified"])


if __name__ == "__main__":
    unittest.main()
