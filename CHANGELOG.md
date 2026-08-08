# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### Added
- feat: add minimal deployment config
- feat(gate): explain surviving mutants in CLI output and CI step summary
- feat: fix frontend UI bugs and add Playwright CI job
- feat: hardening day tasks 1-3 implementation
- feat: setup CI, pre-commit, and introduce a bug in demo-repo

### Fixed
- fix(llm): load .env in CLI, update Gemini model, and add .env.example
- fix(api): harden CORS configuration
- fix: sort imports in app.py

### Changed
- ci: remove unused GitHub pages deployment
- style(api): run ruff format
- chore: pin backend dependencies
- chore: restore load-bearing formatting in demo-repo
- ci: add frontend lint, build and Playwright job with report artifact
- ci: exclude demo-repo fixture from ruff, ignore caches
- chore: add IDE config for pyright/pylance import resolution

### Docs
- docs: fix AGENTS_AND_SKILLS.md to match actual string-based operator implementation
- docs: rewrite README with setup and demo instructions, fix CI badge
- docs: use CONTRACTS.md as single source of truth
- docs: resolve agent tooling mismatch
- docs: update log.txt with hardening day tasks 1-3
