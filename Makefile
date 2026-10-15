SHELL := /bin/bash

# Detecta o interpretador Python (python3 no Linux/macOS, python/py no Windows)
PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || command -v py 2>/dev/null)
INSTALL = $(PYTHON) scripts/install.py

.PHONY: help install-claude install-vscode install-cursor install-codex install-antigravity install-all \
        update-claude update-vscode update-cursor update-codex update-antigravity update-all \
        uninstall-claude uninstall-vscode uninstall-cursor uninstall-codex uninstall-antigravity uninstall-all \
        list test

help:
	@echo "Uso: make <target>"
	@echo ""
	@echo "  install-claude        Claude Code (app e extensão VSCode)  -> ~/.claude/commands"
	@echo "  install-vscode        VSCode Copilot Chat                  -> <User>/prompts"
	@echo "  install-cursor        Cursor                               -> ~/.cursor/commands"
	@echo "  install-codex         Codex CLI/IDE                        -> ~/.codex/prompts"
	@echo "  install-antigravity   Antigravity                          -> ~/.gemini/antigravity/global_workflows"
	@echo "  install-all           Todos os editores"
	@echo "  update-<editor|all>   Reinstala após editar skills/ (mesmo que install)"
	@echo "  uninstall-<editor|all> Remove as skills instaladas"
	@echo "  list                  Lista as skills"
	@echo "  test                  Roda os testes"

install-claude:      ; @$(INSTALL) install claude
install-vscode:      ; @$(INSTALL) install vscode
install-cursor:      ; @$(INSTALL) install cursor
install-codex:       ; @$(INSTALL) install codex
install-antigravity: ; @$(INSTALL) install antigravity
install-all:         ; @$(INSTALL) install all

update-claude: install-claude
update-vscode: install-vscode
update-cursor: install-cursor
update-codex: install-codex
update-antigravity: install-antigravity
update-all: install-all

uninstall-claude:      ; @$(INSTALL) uninstall claude
uninstall-vscode:      ; @$(INSTALL) uninstall vscode
uninstall-cursor:      ; @$(INSTALL) uninstall cursor
uninstall-codex:       ; @$(INSTALL) uninstall codex
uninstall-antigravity: ; @$(INSTALL) uninstall antigravity
uninstall-all:         ; @$(INSTALL) uninstall all

list:
	@$(INSTALL) list

test:
	@$(PYTHON) -m unittest discover -s tests -v

.DEFAULT_GOAL := help
