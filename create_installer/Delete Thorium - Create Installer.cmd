echo off

cd ..

pyinstaller --onefile --icon="C:/ADR_PRODUCTS/BOT/resources/icon_apps/thorium-merah.ico" "./delete_thorium_profiles_gui.py" --name "Delete Thorium Profiles"

pause