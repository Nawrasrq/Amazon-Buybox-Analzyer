@echo off
setlocal enabledelayedexpansion

REM This script handles deployment and execution of the main ETL process:
REM 1.) Captures batch logs to entry_point.log
REM 2.) Changes to project directory
REM 3.) Checks for and activates virtual environment
REM 4.) Updates code from git and installs requirements
REM 5.) Executes the main ETL entry point
