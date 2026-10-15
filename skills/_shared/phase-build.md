## Fase BUILD — gerar o código-fonte e compilar o jogo NATIVO para a plataforma

**O resultado do build é um executável nativo do jogo** (Windows: `.exe`; Linux: binário ELF), **não uma ROM**. A plataforma escolhida em `--platform` define qual executável é gerado e testado (padrão `all` = Windows e Linux). Reconstruir a ROM original não é o objetivo desta fase.

Pré-requisito: `docs/decompiled/` completo (SYSTEM.md, disassembly, `assets/` com `manifest.json`). Se faltar algo, executar antes a fase DECOMPILE (e READ). Esta fase é **autônoma**, como a DECOMPILE: você instala, compila, testa e corrige tudo sem pedir comandos manuais ao usuário; só pergunte em caso de bloqueio real (admin, credenciais).

### 1. Escolher a linguagem / abordagem nativa

Decidir com base no que foi descompilado e registrar a justificativa em `docs/decompiled/SYSTEM.md` (seção "Decisão de build"). Ordem de preferência (usar a de mais alto nível **viável**):

1. **Port em linguagem de alto nível** (C/C++/Rust/Go/etc.): reescrever a lógica do jogo a partir do disassembly, com uma camada de abstração de hardware (vídeo, áudio, entrada, armazenamento) sobre bibliotecas multiplataforma (ex.: SDL2/SDL3, sokol, raylib), carregando os assets extraídos de `docs/decompiled/assets/` (PNG/WAV/JSON), não a ROM.
2. **Recompilação estática** (ex.: N64Recomp, ferramentas de static recompilation 6502/Z80/68k/ARM/MIPS): converter o código descompilado em C/C++ compilado nativamente, com runtime que emula PPU/APU/IO via SDL; assets vêm de `assets/`.
3. **Último recurso:** executável nativo que embute um núcleo de CPU/hardware e executa o código reconstruído a partir de `docs/decompiled/` (montado pelo build, sem depender do arquivo ROM original em `docs/orig/`). Só use se 1 e 2 se mostrarem inviáveis, e registre o motivo.

Toda ferramenta/biblioteca escolhida **precisa existir para Windows e Linux**. O jogo deve rodar completo (todas as telas, fases, áudio e entrada) e não pode ler nada de `docs/orig/` em tempo de execução.

### 2. Gerar o projeto em `src/`

- Código-fonte organizado por módulo (vídeo, áudio, entrada, lógica de jogo, dados), assets em `assets/` (cópia/empacotamento dos extraídos, via `tools/assets_pack.*` quando precisar reconverter).
- Build reprodutível e **multiplataforma**: `CMakeLists.txt` (ou Cargo/Go modules) com presets `windows` e `linux`; `Makefile` e `build.ps1` como atalhos; `tools/bootstrap.(sh|ps1)` que instala toolchain e dependências (SDL etc.) com versões fixas, sem exigir admin quando possível.
- `.github/workflows/build.yml` com matriz `windows-latest` + `ubuntu-latest` (compila, roda os testes e publica o executável como artefato).
- Respeitar `--platform`: se `windows`, gerar/testar só o `.exe`; se `linux`, só o binário Linux; a outra plataforma é registrada como "excluída por filtro".
- Saída em `build/<plataforma>/` (ex.: `build/windows/jogo.exe`, `build/linux/jogo`) com os assets ao lado ou embutidos.

### 3. Compilar, executar e verificar (para cada plataforma selecionada)

1. Build **limpo** na plataforma atual; corrigir erros até compilar sem falhas.
2. **Execução do executável nativo**: iniciar o jogo (modo headless/`--test` com injeção de entrada e captura de frames/áudio, ou display virtual como `xvfb` no Linux), percorrer boot, menu e as fases/telas de forma automatizada e confirmar que roda até o fim sem crash.
3. **Fidelidade em relação ao original:** executar a ROM original em emulador headless (ex.: Mesen, mGBA, BizHawk) com as mesmas entradas e comparar frames/estado (screenshots, hashes de VRAM/RAM em pontos-chave, trilha de áudio). Divergências são bugs a corrigir. Registrar o que não pôde ser comparado automaticamente.
4. **Outra plataforma:** no Windows, compilar e testar a versão Linux via WSL2/Docker; no Linux, compilar Windows (mingw-w64 + Wine, ou CI). Se não for possível localmente, marcar "não verificada localmente" e deixar o workflow de CI pronto; nunca declarar como testada sem ter executado.
5. Repetir até tudo passar; ao esgotar uma estratégia, tentar outra (não pare para sugerir passos manuais).

### 4. Relatório

Gravar `docs/build-report.md`: data, plataformas (verificada local / via CI / filtrada / não verificada), abordagem escolhida e justificativa, versões de ferramentas, comandos exatos para reproduzir, caminhos dos executáveis, resultados dos testes de execução e de fidelidade, e pendências. Terminar listando os executáveis gerados em `build/`.
