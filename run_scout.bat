@echo off
REM Context & Muse — Lead Scout Quick Launcher
cd /d "%~dp0"
uv run python automator.py %*
