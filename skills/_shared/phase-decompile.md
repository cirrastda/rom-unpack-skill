## Fase DECOMPILE — engenharia reversa da ROM

Pré-requisito: `docs/orig/rom-info.json` com o sistema confirmado. Se não existir, executar antes a fase READ. Nunca ler a ROM de fora de `docs/orig/`.

### Modo autônomo (obrigatório)

Esta fase **executa tudo sozinha, até o fim**. É proibido encerrar com sugestões, listas de "próximos passos" ou comandos para o usuário rodar manualmente.

- **Você roda os comandos.** Instale ferramentas, execute disassemblers, escreva e execute scripts. Nunca devolva ao usuário um comando para ele executar.
- **Ferramenta com GUI ou indisponível → use alternativa, não desista.** Ordem de fallback: (1) versão CLI/headless da mesma ferramenta (ex.: Ghidra `analyzeHeadless`); (2) outra ferramenta CLI para a mesma CPU; (3) instalar via `pip`/`npm`/`cargo`/`winget`/`apt`/download de release oficial para `tools/` (ex.: `capstone`, `lief`, `rgbds`, `cc65`, binutils); (4) **escrever o próprio disassembler** em Python (decodificador de opcodes da CPU + varredura recursiva a partir dos vetores/entry point + varredura linear para o restante), pesquisando a tabela de opcodes na Web. Esse último passo sempre é possível, então a fase sempre é concluível.
- **Falhou? Diagnostique e tente de outro jeito**: leia o erro, corrija (dependência, caminho, byte order, header de copiador, mapper) e repita; troque de estratégia após 2 tentativas iguais. Registre as tentativas em `docs/decompiled/SYSTEM.md`.
- **Só pergunte ao usuário** quando houver algo realmente intransponível sem ele: permissão para instalação global que exija admin, credenciais, ou ROM ausente/corrompida. Faça a pergunta única e objetiva, e mesmo assim avance no que for possível.
- **Não reduza o escopo** (ex.: "decompilei só o banco 0"). Processe **todos** os bancos/segmentos/arquivos da ROM.

### Critério de conclusão (a fase só termina quando todos forem verdadeiros)

1. **100% da ROM decompilada, byte a byte.** Cada byte está atribuído a: código disassemblado (instruções com rótulos), dado estruturado (tabela, ponteiros, texto, paleta, gráfico, áudio, mapa — decodificado/extraído para um formato legível com manifesto de offset/tamanho/tipo/compressão) ou padding comprovado (bytes de preenchimento repetidos, ex.: `$00`/`$FF`). Dados comprimidos devem ser descomprimidos (implementar o algoritmo se preciso) e recomprimidos de forma verificável. **`.incbin`/`.byte` opaco só é aceito como etapa intermediária**: ao final, nenhuma região pode ficar como "desconhecida" ou "não classificada". `coverage.md` deve mostrar 100% em código/dado/padding e 0 bytes desconhecidos. Percentual parcial (ex.: 80%, 95%, 99,9%) **não conclui** a fase.
2. **Prova de ida e volta:** a saída de `docs/decompiled/` foi remontada/recompilada por script (`tools/roundtrip.*`) e o resultado tem **SHA1 idêntico** ao de `docs/orig/rom-info.json`. Se divergir, localizar o primeiro offset diferente (`cmp`), corrigir e repetir até igualar. Se o sistema impedir a remontagem byte a byte, remontar o máximo possível e justificar por escrito cada região divergente.
3. `SYSTEM.md`, `SYMBOLS.md` e `coverage.md` existem e refletem o resultado final.
4. **Assets extraídos — entregável obrigatório desta fase, nunca opcional e nunca "a pedido".** `docs/decompiled/assets/` existe, não está vazio e contém **todos** os dados não-código da ROM convertidos para formatos utilizáveis (ver passo 5). Isso é feito na mesma execução do disassembly, sem esperar o usuário pedir.

Se algum critério falhar, **continue trabalhando** em vez de reportar. Só relate o resultado ao usuário quando os quatro estiverem satisfeitos (ou, em caso extremo, após esgotar toda a cadeia de fallback, relatando exatamente o que foi tentado). Dizer "os assets podem ser extraídos depois" ou perguntar se o usuário quer extraí-los é **falha da fase**.

1. **Planejar a toolchain pelo sistema** (pesquisar na Web para confirmar versões atuais e alternativas; esta tabela é só ponto de partida):

| Sistema | CPU | Disassembly / decomp recomendado | Notas |
|---|---|---|---|
| NES / FDS | 6502 | `da65` (cc65), Mesen (debugger + Code/Data Logger), `nesasm`, extração CHR com `tilemolester`/scripts | respeitar mapper e bancos PRG/CHR; separar código de dados via trace do CDL |
| SNES | 65816 | `DiztinGUIsh`, `bsnes-plus` debugger, `snes-disasm`, `wla-65816` | rastrear flags M/X (largura de registradores); LoROM/HiROM |
| Game Boy / GBC | SM83 | `mgbdis`, `rgbds` (`rgbasm`), `pokered`-style disasm | gerar `.asm` por banco e `.inc` de constantes de hardware |
| GBA | ARM7TDMI (ARM/Thumb) | `arm-none-eabi-objdump`, `mgba` debugger, `Ghidra`, `agbcc` para recompilar C | separar ARM/Thumb; mapear IWRAM/EWRAM/IO |
| N64 | MIPS R4300i | `splat` + `Ghidra`, `n64decomp`/`decomp.me`, `mips-linux-gnu-objdump` | converter para z64 (big-endian) antes; checar CIC/boot e overlays |
| NDS | ARM9/ARM7 | `ndstool`, `blz`, `Ghidra`, `ds-decomp` | extrair arm9.bin/arm7.bin/overlays/NitroFS |
| Genesis / 32X / SMS / GG | 68000 / Z80 | `m68k-elf-objdump`, `Ghidra`, `z80dasm`, `clownassembler`/`vasm` | tratar SMD interleaved; vetor de interrupções em 0x0 |
| PC Engine | HuC6280 | `pceas`/`MagicKit`, `Mesen` | remover header de 512 bytes |
| Atari 2600/7800/Lynx | 6502 | `distella`, `da65` | bank switching por tamanho/scheme |
| PlayStation | MIPS R3000 | `Ghidra` (+psx loader), `psx-exe`, `mkpsxiso`/`dumpsxiso`, `splat` | extrair arquivos do ISO primeiro; ler SYSTEM.CNF |
| Saturn / Dreamcast / PSP / 3DS / Wii / GC | variados | `Ghidra`, `dolphin-tool`, `ctrtool`, `PPSSPP` debugger | extrair filesystem antes |
| C64 / ZX / MSX / Amiga / outros | 6502 / Z80 / 68k | `dis6502`, `z80dasm`, `Ghidra` | |

   Se o sistema não estiver na lista, buscar na Web "<sistema> disassembler / reverse engineering / romhacking" e "Ghidra <CPU> processor module".
2. **Preparar o ambiente:** instalar/verificar as ferramentas (convenções, regra 4). Preferir execução headless/linha de comando (ex.: `analyzeHeadless` do Ghidra) para ser reprodutível.
3. **Extrair a estrutura da ROM:** header, tabela de vetores/entry point, bancos/segmentos, filesystem (se houver), mapa de memória do hardware. Separar código de dados (trace dinâmico em emulador headless quando possível; heurísticas estáticas caso contrário).
4. **Disassemblar/descompilar** todo o código alcançável para `docs/decompiled/` organizado por banco/segmento/arquivo (ex.: `bank00.asm`, `main.c`), com:
   - rótulos legíveis para entry points, vetores, handlers de interrupção, rotinas de I/O de hardware e tabelas (renomear conforme o entendimento; manter um `SYMBOLS.md`/`symbols.txt` endereço → nome);
   - constantes de hardware via `.inc`/`.h` (registradores PPU/LCD/DMA etc.);
   - dados binários não-código: ver passo 5 (extração de assets, obrigatória).
5. **Extrair TODOS os assets (obrigatório, na mesma execução):** para cada dado não-código, gerar o arquivo utilizável em `docs/decompiled/assets/<tipo>/`, além do binário bruto:
   - **Gráficos** (tiles, sprites, fontes, backgrounds, telas): PNG com a paleta correta (tilesheets e imagens montadas a partir dos tilemaps), mais JSON com paletas/tilemaps/metasprites;
   - **Áudio** (músicas, efeitos, samples): WAV/OGG para samples e VGM/MIDI/NSF/formato nativo + conversor para sequências; se o formato for proprietário, implementar o decodificador;
   - **Textos/diálogos**: UTF-8 (`.txt`/`.json`) com a tabela de caracteres (`.tbl`) usada;
   - **Tabelas e dados de jogo** (níveis/mapas, inimigos, itens, físicas, ponteiros): JSON/CSV/TMX com campos nomeados;
   - **Dados comprimidos**: descomprimir antes de converter.
   Gerar `docs/decompiled/assets/manifest.json` (offset de origem, tamanho, tipo, compressão, arquivo de saída, arquivo bruto) e um `tools/assets_pack.*` que **reconverte os assets extraídos de volta para os bytes originais** (verificação: bytes idênticos à região de origem). Conferir amostras visualmente quando possível (abrir os PNGs gerados) e corrigir paleta, bitplanes, ordem de tiles ou endianness errados. Pesquisar o formato na Web quando necessário.
   Antes de seguir, validar: `assets/` não vazio, pelo menos um arquivo por tipo existente na ROM, 100% dos intervalos de dados do `coverage.md` presentes no `manifest.json`.
6. **Fechar a cobertura em 100%:** gerar `docs/decompiled/coverage.md` (por banco/segmento: bytes de código, dado, padding, desconhecido) e entrar em loop até **desconhecido = 0**. A cada iteração: listar as regiões desconhecidas, classificá-las (rastrear referências cruzadas de código e ponteiros, trace dinâmico em emulador headless, heurísticas de entropia/padrão para detectar compressão, gráficos, áudio, texto e tabelas, pesquisa na Web do formato) e reprocessar. Manter `.incbin` apenas temporário para não perder bytes entre iterações; ao final, substituir por código/dado decodificado.
7. **Gravar `docs/decompiled/SYSTEM.md`:** sistema, CPU, mapper/variante, ferramentas e versões usadas, URLs de documentação, mapa de memória, pontos de entrada, decisões e incertezas, e **recomendação de linguagem/toolchain** para a fase BUILD (ver critérios lá).
8. **Executar o round-trip** do critério de conclusão e corrigir até o SHA1 bater.
9. **Saída:** resumo com cobertura, assets extraídos (contagem por tipo), resultado do round-trip (SHA1 original vs. remontado), principais rotinas identificadas, riscos (ex.: compressão proprietária, código auto-modificável) e o caminho de `docs/decompiled/`. Sem lista de passos manuais para o usuário.
