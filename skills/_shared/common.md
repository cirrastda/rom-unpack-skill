## Convenções do projeto (valem para todas as fases)

**Argumentos recebidos:** {{ARGS}}

Flags aceitas (todas opcionais):
- `--rom=<caminho>`: ROM de entrada. Se omitida, usar a anexada/mencionada no chat ou o único arquivo em `docs/orig/`.
- `--system=<nome>`: força o sistema e pula a identificação automática.
- `--platform=windows|linux|all`: limita o build a uma plataforma (padrão: `all`).
- `--lang=<c|asm|python|...>`: força a linguagem-alvo da fonte reconstruída.

### Estrutura de pastas (relativa à raiz do projeto de destino)

```
docs/orig/            ROM original (nunca modificar) + rom-info.json (hashes, sistema, header)
docs/decompiled/      saída da engenharia reversa (disassembly, assets/ extraídos + manifest.json, SYSTEM.md, SYMBOLS.md, coverage.md)
docs/build-report.md  resultado dos testes de build/execução por plataforma
src/                  código-fonte reconstruído (linguagem escolhida)
build/                executáveis nativos por plataforma (build/windows, build/linux; ignorar no git)
Makefile, build.ps1   build reprodutível (Linux/macOS via make, Windows via PowerShell ou make)
.github/workflows/build.yml   matriz windows-latest + ubuntu-latest
```

### Regras gerais

1. **Estado entre fases:** cada fase deve gravar seu progresso em arquivos (`rom-info.json`, `docs/decompiled/SYSTEM.md`, `docs/build-report.md`) para que a próxima fase, ou outra sessão, retome sem repetir trabalho. Ao iniciar, ler o que já existe e só refazer o que faltar ou estiver desatualizado (comparar SHA1 da ROM em `rom-info.json`).
2. **Nunca alterar `docs/orig/`.** Ela é a fonte da verdade para verificação byte a byte.
3. **Pesquisar na Web** (documentação do hardware, Data Crisis/Romhacking.net, GitHub, projetos `*-disasm`/`*-decomp`, Pan Docs, SNESdev/NESdev wiki, Sega Retro, GBATEK etc.) sempre que faltar conhecimento sobre mapa de memória, formato de arquivo, mapper, compressão ou toolchain. Registrar as URLs úteis em `docs/decompiled/SYSTEM.md`. Verificar se já existe um disassembly/decomp público do mesmo jogo (busca por título + hash) e, se existir, usá-lo como referência (citar a fonte), nunca como substituto da verificação contra a ROM.
4. **Instalar ferramentas** necessárias de forma local e reprodutível (preferir gerenciadores: `winget`/`choco`/`scoop` no Windows, `apt`/`brew` no Linux, ou baixar release oficial para `tools/`). Antes de instalar algo global, avisar o usuário. Documentar versões em `docs/decompiled/SYSTEM.md`.
5. **Ferramenta auxiliar de identificação:** `python ~/.rom-unpack/rom_identify.py <rom> [--copy-to docs/orig]` (no Windows: `python "$env:USERPROFILE\.rom-unpack\rom_identify.py"`). Se não existir, identificar manualmente (extensão, magic bytes, cabeçalho) e criar `rom-info.json` com os mesmos campos.
6. **Honestidade nos resultados:** só declarar "build OK", "roda completo" ou "idêntico ao original" depois de executar e comparar de fato. Se algo não puder ser testado (ex.: sem emulador, sem acesso ao outro SO), dizer explicitamente o que ficou sem verificação e como verificar.
7. **Aspectos legais:** a ROM e os assets extraídos são conteúdo protegido. Garantir que `docs/orig/` e `docs/decompiled/` (assets) estejam no `.gitignore` caso o repositório seja público, e avisar o usuário. Não baixar ROMs da Web.
8. Responder ao usuário em português, de forma concisa, finalizando com o resumo do que foi feito, caminhos gerados e próximos passos.
