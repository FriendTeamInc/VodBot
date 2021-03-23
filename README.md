# <img src="/assets/vodbot_logo.png" alt="VodBot" height="100" /> by NotQuiteApex & FTI.
A VOD and clip manager for Twitch. Downloads VODs and clips with appropriate metadata for any public channel.

# Installation and Usage
Requirements:
* [Python 3.6+](https://www.python.org/)
* [Streamlink](https://github.com/streamlink/streamlink)

VodBot can be installed with `pip install .`, running it will write a config file and associated folder in your home directory (`~` on UNIX systems, `C:\Users\%USERNAME%\` on Windows). You'll need to fill out the config before continuing the program with your Twitch app's Client ID and Secret, along with the names of the channels you want to watch for VODs.

Running `vodbot vods` or `vodbot clips` will download the vods or clips of the channels you have set to watch in your config file. It's recommended that if you plan to use this for the long term to save the videos in some kind of redundant storage array or in multiple locations (or both).

Metadata contains date (in UTC), the user that streamed, the title, and the video ID. Clips have all that info in addition to clip author and view count.

It is recommended that you run VodBot with some kind of scheduling program like systemd or cron every so often to pull the VODs for you.

# License
This project is licensed under the zlib license, copyright Logan "NotQuiteApex" Hickok-Dickson. See LICENSE.md for more details.
