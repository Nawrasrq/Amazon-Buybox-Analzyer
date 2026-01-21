@echo off
setlocal enabledelayedexpansion

REM This script launches GUI tools for manual ETL operations:
REM 1.) Captures batch logs to tool.log
REM 2.) Changes to project directory
REM 3.) Checks for and activates virtual environment
REM 4.) Updates code and dependencies (optional)
REM 5.) Launches the specified GUI tool