@echo off
REM Run PyInstaller with the spec file
pyinstaller HetLuxLab.spec --no-confirm

REM Copy the Excel file to the dist folder
copy /Y real_data.xlsx dist\LuxLabApp\

REM Copy the icons folder recursively to the dist folder
xcopy /E /I /Y icons dist\LuxLabApp\icons

echo Build and copy done!
pause
