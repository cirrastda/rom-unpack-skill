## Fase FIX — corrigir um problema reportado e rebuildar

O texto dos argumentos (exceto flags) descreve o problema: o que não funciona, onde e como reproduzir. Se estiver vazio, pedir em uma linha a descrição do problema e parar.

1. **Entender o relato:** reformular o sintoma, o comportamento esperado e o critério de aceite (ex.: "SHA1 volta a bater", "tela X renderiza igual ao original", "build Linux compila").
2. **Reler as fontes da verdade**, nesta ordem:
   - `docs/orig/` (ROM original + `rom-info.json`) — o que o jogo realmente faz;
   - `docs/decompiled/` (disassembly, `SYMBOLS.md`, `SYSTEM.md`, assets, `coverage.md`);
   - `src/`, `Makefile`/`build.ps1`, `docs/build-report.md` e logs do último build.
3. **Reproduzir** o problema (build, `verify`, execução em emulador). Classificar a causa: (a) erro de build/toolchain, (b) divergência de bytes (localizar primeiro offset divergente e mapear para o símbolo), (c) erro de comportamento na execução (comparar traço/frames/estado com a ROM original em emulador), (d) problema específico de SO (caminhos, fim de linha, case-sensitivity, ferramenta indisponível).
4. **Se a decompilação estiver errada ou incompleta** (código classificado como dado, tamanho de operando errado, banco/mapper incorreto, asset mal extraído): corrigir primeiro em `docs/decompiled/` (refazendo só o trecho afetado a partir da ROM em `docs/orig/`), atualizar `SYMBOLS.md`/`coverage.md`, e então propagar para `src/`. Pesquisar na Web documentação do hardware quando a causa envolver comportamento específico.
5. **Corrigir** com a menor mudança possível, sem refatorações alheias ao problema. Não editar `docs/orig/`.
6. **Rebuildar e verificar** (build limpo, fidelidade SHA1, testes de execução, ambas as plataformas conforme `--platform`). Confirmar o critério de aceite do passo 1 e que nada que passava antes quebrou.
7. **Registrar:** atualizar `docs/build-report.md` (seção "Correções": problema, causa raiz, arquivos alterados, evidência de verificação). Se a causa não for encontrada ou a correção não puder ser verificada, dizer isso claramente, com hipóteses e próximos passos.
