@echo off
::
:: Windows Cmd script to run all parsers one after another.
::
:: @author: nrekow
::
setlocal
set DESTINATION=D:\Downloads\parsers
set SCRIPTPATH=%~dp0
cd %SCRIPTPATH:~0,-1%
:: echo %SCRIPTPATH:~0,-1%
for %%P in (cnh,dilbert,xkcd) do (py %%P\%%P.py -o %DESTINATION%\%%P)
bash /mnt/d/Downloads/parsers/maloney.sh /mnt/d/Downloads/parsers/maloney
endlocal