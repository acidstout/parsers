@echo off
::
:: Windows Cmd script to run all parsers one after another.
::
:: @author: nrekow
::
setlocal
set SCRIPTPATH=%~dp0
cd %SCRIPTPATH:~0,-1%
echo %SCRIPTPATH:~0,-1%
for %%P in (cnh,dilbert,xkcd) do (py %%P\%%P.py -o %USERPROFILE%\Downloads\parsers\%%P)
endlocal