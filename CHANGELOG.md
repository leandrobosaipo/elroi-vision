# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2025.01.XX]
### Fixed
- Correção de serialização JSON: conversão explícita de tipos numpy (uint8, int32, float32, etc.) para tipos Python nativos (int, float)
- Garantia de que todos os valores retornados pelos serviços de neuromarketing são serializáveis pelo FastAPI

### Changed
- Serviços atualizados para converter explicitamente valores numpy antes de retornar: colors.py, texture.py, scene.py, lighting.py, depth.py, saliency.py, emotion.py, cta.py
- Função orquestradora `analyze_neuromarketing` atualizada para garantir tipos Python puros

## [2023.2.20]
### ADD
- pytest coverage
### Changed
- update version ultralytics

## [2023.1.31]
### ADD
- Start Repo