## Fase BUILD — gerar o código-fonte de rebuild e compilar (Windows e Linux)

Pré-requisito: `docs/decompiled/SYSTEM.md` e os arquivos descompilados. Se não existirem, executar antes a fase DECOMPILE (e READ).

### 1. Escolher a linguagem / abordagem

Decidir com base no que foi descompilado e registrar a justificativa em `docs/decompiled/SYSTEM.md` (seção "Decisão de build"). Ordem de preferência (usar o mais alto nível **viável**, sem sacrificar a fidelidade verificável):

1. **Linguagem de alto nível (C/C++/Rust/etc.)** quando houver decomp matching/boa cobertura de lógica reconhecível (comum em N64/PSX/GBA/NDS com compilador conhecido, ou quando uma reimplementação portável, ex.: C + SDL2, for viável). Se o compilador original for conhecido, usar o mesmo (ex.: `agbcc`, IDO, GCC antigo) para obter ROM idêntica.
2. **Assembly com assembler cross-platform** (RGBDS, ca65/ld65, WLA-DX, vasm, armips, `arm-none-eabi-as`, `m68k-elf-as`) quando a decompilação em alto nível não for viável. É o caminho padrão para NES/SNES/GB/GBC/Genesis/SMS/PCE/Atari.
3. **Binários + `.incbin`** para partes não decompiláveis (dados, áudio, código ainda não entendido), sempre com manifesto de offsets.

Todas as ferramentas escolhidas **precisam existir para Windows e Linux** (ou ser compiláveis delas). Se uma não existir para um dos SOs, trocar por alternativa ou compilar a partir do código-fonte durante o build.

Resultado esperado de "build": a **ROM reconstruída** (mesmo formato do original). "Rodar completo" significa executar a ROM reconstruída em emulador (preferir o headless/CLI) no Windows e no Linux, e/ou, no caso de port nativo, o executável gerado.

### 2. Gerar o projeto em `src/`

- Converter o conteúdo de `docs/decompiled/` em fontes organizados (um arquivo por banco/módulo), `include/` com constantes, `assets/` com binários referenciados.
- Criar o build reprodutível:
  - `Makefile` (alvos `all`, `rom`, `verify`, `test`, `clean`) que funcione em Linux e em Windows (via MSYS2/Git Bash/`make` do Chocolatey);
  - `build.ps1` equivalente para Windows sem `make`;
  - um `tools/bootstrap.(sh|ps1)` que baixa/instala as versões fixas das ferramentas em `tools/` (sem exigir privilégios de admin quando possível);
  - `.github/workflows/build.yml` com matriz `windows-latest` + `ubuntu-latest` que roda bootstrap, build, `verify` e teste de execução.
- Respeitar `--platform`: se `windows` ou `linux`, gerar/testar só essa plataforma e registrar que a outra foi excluída por filtro.

### 3. Compilar e verificar

1. Rodar o build **limpo** na plataforma atual.
2. **Verificação de fidelidade:** comparar o SHA1/CRC32 da ROM gerada com o de `docs/orig/rom-info.json` (`cmp`/`Get-FileHash`). Meta: idêntica byte a byte. Se houver diferença, localizar o primeiro offset divergente (`cmp -l | head`), mapear para o símbolo/banco e corrigir. Se a identidade total for impossível (ex.: port em C), documentar o critério de equivalência usado (ex.: testes de saída de vídeo/áudio/estado por frames).
3. **Teste de execução completo:** rodar a ROM em emulador headless/CLI (ex.: Mesen `--testrunner`, mGBA `-t`/scripting, BizHawk/Lua, Ares/higan, melonDS, PPSSPP, Dolphin) por tempo suficiente para passar por boot, menu e gameplay inicial, com script que automatize inputs e capture screenshot/hash de frames; comparar com a execução da ROM original nos mesmos inputs. "Completo" significa percorrer o jogo na medida do automatizável; o que não for coberto deve ser listado em `docs/build-report.md` com instruções de verificação manual.
4. **Outra plataforma:** se estiver no Windows, testar Linux via WSL2/Docker; se estiver em Linux, testar Windows via cross-compile + Wine, VM ou CI. Se não for possível localmente, disparar/descrever o workflow de CI e marcar a plataforma como "não verificada localmente".
5. Corrigir falhas e repetir até passar. Máximo de tentativas autônomas razoáveis: se travar, reportar o bloqueio e as hipóteses em vez de forçar.

### 4. Relatório

Gravar `docs/build-report.md` com: data, plataformas (Windows/Linux: verificado local / via CI / filtrado / não verificado), versões de ferramentas, comandos exatos para reproduzir, SHA1 original vs. gerado, resultado dos testes de execução e pendências.
