@echo off

rem Enter the temporary site construction directory
cd "%3"

rem Remove existing site data if it exists
rmdir /Q /S tmp_env > nul 2> nul
rmdir /Q /S "%2" > nul 2> nul
