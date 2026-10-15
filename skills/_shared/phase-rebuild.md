## Fase REBUILD — reconstruir o executável nativo a partir do que já existe

Objetivo: refazer o build **nativo e limpo** (executável por plataforma, não ROM) e revalidar tudo, sem redescobrir a engenharia reversa.

1. Ler `docs/orig/rom-info.json`, `docs/decompiled/SYSTEM.md`, `docs/decompiled/assets/manifest.json`, `docs/build-report.md` (se houver) e o conteúdo de `src/`.
2. Se `docs/orig/` não tiver a ROM, ou o SHA1 não bater com `rom-info.json`: parar e avisar. Se `docs/decompiled/` (incluindo `assets/`) ou `src/` estiverem ausentes, executar as fases DECOMPILE e BUILD completas; se existirem, **não** descompilar de novo.
3. Limpar artefatos (`make clean` ou remover `build/`), reinstalar/validar ferramentas via `tools/bootstrap`, e rodar o build nativo completo para as plataformas de `--platform` (padrão: Windows e Linux).
4. Repetir os testes de execução e de fidelidade (comparação com a ROM original em emulador) conforme a fase BUILD.
5. Atualizar `docs/build-report.md` com o novo resultado e mostrar o diff em relação ao relatório anterior (passou/quebrou). Se algo quebrou, investigar e corrigir seguindo a fase FIX em vez de apenas reportar.
