# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.9.1](https://github.com/meramsey/wizardwebssh/releases/tag/1.9.1) - 2022-04-02

<small>[Compare with 1.9.0](https://github.com/meramsey/wizardwebssh/compare/1.9.0...1.9.1)</small>


## [1.9.0](https://github.com/meramsey/wizardwebssh/releases/tag/1.9.0) - 2022-03-31

<small>[Compare with 1.8.0](https://github.com/meramsey/wizardwebssh/compare/1.8.0...1.9.0)</small>

### Bug Fixes
- switch palette colors from pyqt6 to pyqt5 enums ([7cfb558](https://github.com/meramsey/wizardwebssh/commit/7cfb558b7033471e45d6559bdcfc2f5eeea205f4) by Michael Ramsey).
- update dependency tomlkit to v0.10.0 ([15c96e8](https://github.com/meramsey/wizardwebssh/commit/15c96e87b3e182226767170fc043abf25c0c4e59) by Renovate Bot).
- fix mkdocs error upon pw build by changing check_docs to check-docs ([b0dda3c](https://github.com/meramsey/wizardwebssh/commit/b0dda3cf7a7b1015aec973d7b89e706116ec371d) by Michael Ramsey).
- pinned dependencies that were missing ([d40f113](https://github.com/meramsey/wizardwebssh/commit/d40f113343603e1c27d6c3ad6999bb48f388c088) by Michael Ramsey).
- ci errors due to pyqt6 not being an extra now ([cdcd539](https://github.com/meramsey/wizardwebssh/commit/cdcd53975f0392d0e7a17dbd0e669b711dc1fd00) by Michael Ramsey).

### Features
- downgrade dependencies from pyqt6 to pyqt5 ([75b8169](https://github.com/meramsey/wizardwebssh/commit/75b8169d32b0f3dfa6418100455536df8ebc0bd4) by Michael Ramsey).


## [1.8.0](https://github.com/meramsey/wizardwebssh/releases/tag/1.8.0) - 2022-02-08

<small>[Compare with 1.7.5](https://github.com/meramsey/wizardwebssh/compare/1.7.5...1.8.0)</small>

### Bug Fixes
- commit missing poetry.lock and poetry.toml ([1b2a4ea](https://github.com/meramsey/wizardwebssh/commit/1b2a4ea2e60fd7263b56a206c0c9c1793401f684) by Michael Ramsey).

### Features
- Setup project to use pyprojectx for stuff in preparation to eventually replace duties. ([1cbd658](https://github.com/meramsey/wizardwebssh/commit/1cbd6583abf09cee549ce77dd1753fb536c6b845) by Michael Ramsey).


## [1.7.5](https://github.com/meramsey/wizardwebssh/releases/tag/1.7.5) - 2022-02-06

<small>[Compare with 1.7.4](https://github.com/meramsey/wizardwebssh/compare/1.7.4...1.7.5)</small>

### Bug Fixes
- remove dead code ([52b928c](https://github.com/meramsey/wizardwebssh/commit/52b928c334b1812802538d53d5d3da3e527b4569) by Michael Ramsey).
- Update FUNDING.yml with proper information ([5c42ac9](https://github.com/meramsey/wizardwebssh/commit/5c42ac93b52e2a5a6c699bdebeaf0da2a198be5b) by Michael Ramsey).
- remove the tabbedterminal.md since its breaking docs in CI setting ([a667007](https://github.com/meramsey/wizardwebssh/commit/a667007551e41d096cdd1a6cdc6923c89852f3dd) by Michael Ramsey).
- Update tabbedterminal.py for  PyQT issues in CI take2 ([c0fe0e5](https://github.com/meramsey/wizardwebssh/commit/c0fe0e5b21ab14f15339000e64aa4358866986f1) by Michael Ramsey).
- Update tabbedterminal.py for  PyQT issues in CI ([74f9aba](https://github.com/meramsey/wizardwebssh/commit/74f9abac6a96817a35975c9c12ea61bd4bf7e16e) by Michael Ramsey).
- Update handler.py for other PyQT issues in CI and formatting take 3 ([22a72e1](https://github.com/meramsey/wizardwebssh/commit/22a72e127fc4452a43e170279319734f7d55b4e0) by Michael Ramsey).
- fix extras imports for ci and add docstrings to handler.py ([98a1b50](https://github.com/meramsey/wizardwebssh/commit/98a1b50940a050467c7393c8f033912d9bfe7f70) by Michael Ramsey).
- Update handler.py for ci issues ([d9b2130](https://github.com/meramsey/wizardwebssh/commit/d9b2130b8a68edf17af301b5c7ecd73bf0a4c9e7) by Michael Ramsey).

## [1.7.4](https://github.com/meramsey/wizardwebssh/releases/tag/1.7.4) - 2022-02-06

<small>[Compare with 1.7.3](https://github.com/meramsey/wizardwebssh/compare/1.7.3...1.7.4)</small>

### Bug Fixes
- Update Readme title ([9b2fa15](https://github.com/meramsey/wizardwebssh/commit/9b2fa158dd4ec31abff87c3179baef2bfd2fa0bb) by Michael Ramsey).
- changelog and duties.py to start at 1.7.4 for next version ([57e434a](https://github.com/meramsey/wizardwebssh/commit/57e434ac53e36001e4875473ac941b1e8b33f9c9) by Michael Ramsey).

### Features
- refactored ([ffe1d1b](https://github.com/meramsey/wizardwebssh/commit/ffe1d1b6d971971509be513a1d8d9ceebfc70e5b) by Michael Ramsey).

## [1.7.3](https://github.com/meramsey/wizardwebssh/releases/tag/1.7.3) - 2022-02-06

<small>[Compare with first commit](https://github.com/meramsey/wizardwebssh/compare/d24e6f4b4078969950c70b1e0d2626f90bf1cd05...1.7.3)</small>

### Features
- bump dependencies for pyqt5 to pyqt6 ([0e44c6e](https://github.com/meramsey/wizardwebssh/commit/0e44c6e9b2eead7509d2a1715f39fd8d7bfb04c0) by Michael Ramsey).
- bump depends for xterm bootstrap popper ([6be2d5a](https://github.com/meramsey/wizardwebssh/commit/6be2d5a2e15a70a81d7000eb2e14626ea478e6bc) by Michael Ramsey).
