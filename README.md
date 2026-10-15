# rom-unpack

Skills de IA para **ler, descompilar e rebuildar ROMs de jogos** (Windows e Linux), instaláveis com um único `make` em:

| Editor | Destino da instalação | Como invocar |
|---|---|---|
| Claude Code (app, CLI e extensão VSCode) | `~/.claude/commands/` | `/read-rom` |
| VSCode (GitHub Copilot Chat, modo agente) | `<User>/prompts/*.prompt.md` | `/read-rom` |
| Cursor | `~/.cursor/commands/` | `/read-rom` |
| Codex (CLI e IDE) | `~/.codex/prompts/` (respeita `CODEX_HOME`) | `/prompts:read-rom` |
| Antigravity | `~/.gemini/antigravity/global_workflows/` | `/read-rom` |

`<User>` do VSCode: `%APPDATA%\Code\User` (Windows), `~/Library/Application Support/Code/User` (macOS), `~/.config/Code/User` (Linux). O VSCode Insiders também é atendido se existir.

## Pré-requisitos

- Python 3.8+ (somente biblioteca padrão)
- `make` (opcional; sem ele, use o comando `python scripts/install.py ...` equivalente)
- O editor de destino já aberto ao menos uma vez

## Instalação

```bash
git clone <url-deste-repositorio> rom-unpack
cd rom-unpack

make install-all           # todos os editores
# ou apenas um:
make install-claude
make install-vscode
make install-cursor
make install-codex
make install-antigravity
```

Sem `make` (ex.: Windows puro):

```powershell
python scripts/install.py install all          # ou: claude | vscode | cursor | codex | antigravity
```

Depois reinicie o editor (VSCode: `Ctrl+Shift+P` > `Developer: Reload Window`; Cursor/Antigravity/Codex: reabrir; Claude Code: nova sessão).

Outros alvos: `make update-<editor|all>` (reinstala após editar `skills/`), `make uninstall-<editor|all>`, `make list`, `make test`, `make help`.

A instalação também copia `tools/rom_identify.py` para `~/.rom-unpack/` (identificador de sistema usado pelas skills).

## Skills

| Comando | O que faz |
|---|---|
| `/read-rom` | Identifica o sistema (extensão, magic bytes, hash na Web; pergunta se não conseguir) e salva a ROM em `docs/orig/` com `rom-info.json`. |
| `/decompile-rom` | Lê a ROM de `docs/orig/` e faz a engenharia reversa para `docs/decompiled/` (disassembly, símbolos, assets, cobertura, `SYSTEM.md`). |
| `/build-rom` | Lê o decompilado, escolhe a melhor linguagem (alto nível quando viável; senão C/Assembly/binários), gera `src/`, builda e testa em Windows e Linux. |
| `/read-and-decompile-rom` | read + decompile |
| `/read-and-build-rom` | read + decompile + build |
| `/decompile-and-build-rom` | decompile + build |
| `/rebuild-rom` | Build limpo a partir do que já existe, revalidando contra a ROM original. |
| `/fix-rom-and-build` | Recebe o problema, relê `docs/orig/` e `docs/decompiled/`, corrige e rebuilda com verificação. |

Flags (opcionais): `--rom=<caminho>`, `--system=<nome>`, `--platform=windows|linux|all`, `--lang=<c|asm|...>`.

### Exemplos

```
/read-and-build-rom --rom=C:\roms\jogo.gba
/build-rom --platform=linux
/fix-rom-and-build o jogo trava na tela de título depois do logo --platform=all
```

## Layout gerado no projeto do jogo

```
docs/orig/           ROM original (imutável) + rom-info.json
docs/decompiled/     disassembly, assets, SYMBOLS.md, SYSTEM.md, coverage.md
docs/build-report.md resultado dos builds/testes por plataforma
src/  build/  Makefile  build.ps1  .github/workflows/build.yml
```

Execute as skills na raiz de um projeto vazio (ou do jogo). Um build só é declarado OK após verificação real (SHA1 da ROM gerada vs. original e execução em emulador); plataformas não testáveis localmente são marcadas como tal em `docs/build-report.md`.

## Como funciona / como editar

Fonte única em `skills/`: `skills.json` (nome, descrição, fases) + `skills/_shared/` (`common.md` e uma fase por arquivo). `scripts/install.py` compõe cada skill (as combinadas, como `read-and-build-rom`, concatenam as fases) e grava no formato de cada editor. Para alterar o comportamento, edite as fases e rode `make update-all`.

## Aviso legal

ROMs e assets extraídos são conteúdo protegido por direitos autorais. Use apenas ROMs que você possui legalmente e não publique `docs/orig/` nem `docs/decompiled/` (já estão no `.gitignore` deste repositório; replique no projeto do jogo).
