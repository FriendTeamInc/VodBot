# VodBot
A VOD manager for Twitch to Youtube, written in Python, that keeps copies and uploads them to YouTube.

# Installation and Usage
Requirements:
* [Python 3.6+](https://www.python.org/)
* [Streamlink](https://github.com/streamlink/streamlink)

VodBot can be installed with `pip install .`, running it will write a config file and associated folder in your home directory (`~` on UNIX systems, `C:\Users\%USERNAME%\` on Windows). You'll need to fill out the config before continuing the program with your Twitch app's Client ID and Secret, along with the names of the channels you want to watch for VODs. After that, everytime VodBot is ran it will search Twitch for VODs it does not have from the channels you're watching.

It is recommended that you run VodBot with some kind of scheduling program like systemd or cron every so often to pull the VODs for you.

# License
This project is licensed under the zlib license, copyright Logan "NotQuiteApex" Hickok-Dickson. See LICENSE.md for more details.
