## Fase DECOMPILE — engenharia reversa da ROM

Pré-requisito: `docs/orig/rom-info.json` com o sistema confirmado. Se não existir, executar antes a fase READ. Nunca ler a ROM de fora de `docs/orig/`.

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
   - dados binários não-código (gráficos, áudio, tabelas, textos) extraídos como arquivos em `docs/decompiled/assets/` com manifesto (offset, tamanho, tipo, compressão).
5. **Verificar a cobertura:** garantir que cada byte da ROM está atribuído a código, dado ou padding (gerar `docs/decompiled/coverage.md` com % por banco e regiões não classificadas). Regiões não classificadas devem ser mantidas como `.incbin` para não perder bytes.
6. **Gravar `docs/decompiled/SYSTEM.md`:** sistema, CPU, mapper/variante, ferramentas e versões usadas, URLs de documentação, mapa de memória, pontos de entrada, decisões e incertezas, e **recomendação de linguagem/toolchain** para a fase BUILD (ver critérios lá).
7. **Saída:** resumo com cobertura, principais rotinas identificadas, riscos (ex.: compressão proprietária, código auto-modificável) e o caminho de `docs/decompiled/`.
