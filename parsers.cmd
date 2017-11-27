@echo off
::
:: Windows Cmd script to run all parsers one after another.
::
:: @author: nrekow
::
setlocal
set DESTINATION=U:\Downloads\parsers
set SCRIPTPATH=%~dp0
cd %SCRIPTPATH:~0,-1%
:: echo %SCRIPTPATH:~0,-1%
for %%P in (cnh,dilbert,xkcd) do (py %%P\%%P.py -o %DESTINATION%\%%P)
echo "Checking for new Philip Maloney episodes ..."
bash /mnt/d/Downloads/maloney.sh
endlocal