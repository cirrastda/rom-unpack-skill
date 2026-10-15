## Fase READ — ler e arquivar a ROM

Objetivo: identificar o sistema da ROM e salvá-la em `docs/orig/`. **Esta fase não descompila nada.**

1. **Localizar a ROM** (`--rom`, anexo, ou arquivo mencionado). Se não houver nenhuma, pedir o caminho em uma linha e parar.
2. **Se for arquivo compactado** (`.zip`, `.7z`, `.chd`, `.rvz`): extrair para um diretório temporário, usar o conteúdo relevante e registrar o nome original em `rom-info.json` (`container`). Para discos (`.cue/.bin`, `.iso`), manter todos os arquivos do conjunto em `docs/orig/`.
3. **Identificar o sistema** (pular se `--system` foi passado):
   - Rodar o `rom_identify.py` com `--copy-to docs/orig` (ver convenções).
   - Conferir o resultado com a Web: buscar o formato pela extensão + assinatura (ex.: "iNES header", "GBA ROM header logo 0xB2 0x96", "Mega Drive ROM header") e, se possível, o hash (SHA1/CRC32) em bases como No-Intro, Redump, Hasheous ou Data Crisis para confirmar título/região/revisão.
   - Se `identified` for `false`, houver candidatos empatados ou a extensão for ambígua (`.bin`, `.rom`, `.img`): **perguntar ao usuário qual é o sistema** (listar os candidatos como opções) e aguardar a resposta antes de continuar. Nunca chutar.
4. **Registrar** em `docs/orig/rom-info.json`: arquivo, tamanho, crc32/md5/sha1/sha256, sistema confirmado, como foi confirmado (header/hash/usuário), título, região, mapper/variante, byte order (N64), cabeçalho de copiador presente.
5. **Saída:** exibir uma tabela curta (sistema, título, região, tamanho, SHA1, nível de confiança) e o caminho `docs/orig/<rom>`.
