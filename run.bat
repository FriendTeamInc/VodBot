@echo off
REM For quick-testing the bot!
pip3 uninstall vodbot -y >NUL && pip3 install . >NUL && vodbot -h