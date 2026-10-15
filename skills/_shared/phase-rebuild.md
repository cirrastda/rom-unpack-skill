## Fase REBUILD — reconstruir a partir do que já existe

Objetivo: refazer o build **limpo** e revalidar tudo, sem redescobrir a engenharia reversa.

1. Ler `docs/orig/rom-info.json`, `docs/decompiled/SYSTEM.md`, `docs/build-report.md` (se houver) e o conteúdo de `src/`.
2. Se `docs/orig/` não tiver a ROM, ou o SHA1 não bater com `rom-info.json`: parar e avisar. Se `docs/decompiled/` ou `src/` estiverem ausentes, executar as fases DECOMPILE e BUILD completas; se existirem, **não** descompilar de novo.
3. Limpar artefatos (`make clean` ou remover `build/`), reinstalar/validar ferramentas via `tools/bootstrap`, e rodar o build completo.
4. Repetir a verificação de fidelidade (SHA1/CRC32 vs. original) e os testes de execução nas plataformas definidas por `--platform` (padrão: Windows e Linux), conforme a fase BUILD.
5. Atualizar `docs/build-report.md` com o novo resultado e mostrar o diff em relação ao relatório anterior (passou/quebrou). Se algo quebrou, listar o primeiro ponto de falha e sugerir `/fix-rom-and-build`.
