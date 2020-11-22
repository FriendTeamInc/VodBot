# VodBot
A VOD manager for Twitch to Youtube, written in Python, that keeps copies and uploads them to YouTube.

# Installation and Usage
Requirements:
* [Python 3.6+](https://www.python.org/)
* [Streamlink](https://github.com/streamlink/streamlink)

For now, the program can be installed with the `pip install .` command after cloning the repo. Running `vodbot` for the first time will generate a `.vodbot` directory in your home directory, located at `~` on UNIX platforms and `C:\Users\%USERNAME%\` on Windows. You must fill out the `config.toml` file inside this directory before the app will run. VodBot is intended to be ran by some sort of scheduling program and never directly, like systemd or chron, however it can run as an immediate program and will not function differently.

# License
This project is licensed under the zlib license, copyright Logan "NotQuiteApex" Hickok-Dickson. See LICENSE.md for more details.
