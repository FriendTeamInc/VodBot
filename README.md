# <img src="/banner.png" alt="VodBot" height="100" /> by NotQuiteApex & FTI.
A VOD and clip manager for Twitch. Downloads VODs and clips with appropriate metadata for any public channel.

## Project Status
This project is a heavy Work-In-Progress, and lots of changes can occur before an inevitable "release". This project is largely for my own uses and needs, and isn't intended for general use. For progress and roadmap, check the [projects page](https://github.com/NotQuiteApex/VodBot/projects).

# Installation
Requirements:
* [Python 3.5+](https://www.python.org/)
* [Requests 2.20+](https://requests.readthedocs.io/en/master/)
* [M3U8 0.8+](https://github.com/globocom/m3u8)
* [ffmpeg](https://www.ffmpeg.org/) (Must be in PATH)

VodBot can be installed with `pip install .`, running it will write a config file and associated folder in your home directory (`~` on UNIX systems, `C:\Users\%USERNAME%\` on Windows). You'll need to fill out the config before continuing the program with your Twitch app's Client ID and Secret, along with the names of the channels you want to watch for VODs.

The Makefile in the repo can be used, though it is simply a shorthand script for rapid testing the program for the devs.

# Usage
If it hasn't been run before, simply run `vodbot` to initialize directories and files.

Running `vodbot vods` or `vodbot clips` will download the vods or clips of the channels you have set to watch in your config file. It's recommended that if you plan to use this for the long term to save the videos in some kind of redundant storage array or in multiple locations (or both).

Metadata json files contain the date (in UTC), the user that streamed, the title, and the video ID. Clips metadata have all that info in addition to clip author and view count.

It is recommended that you run VodBot with some kind of scheduling program like `systemd` or `cron` every so often to pull the VODs and clips for you.

# Configurations
These are the default config files for the services used by VodBot.

`twitch-conf.json` - Channels to watch for VODs and clips, and where to save them to.
```json
{
  "channels": [
    "alkana", "batkigu", "hylianswordsman1"
    "juicibit", "michiri9", "notquiteapex",
    "pissyellowcrocs", "percy_creates", "voobo",
    "46moura",
  ],

  "client_id": "[[INSERT CLIENT ID HERE]]",
  "client_secret": "[[INSERT CLIENT SECRET HERE]]",

  "vod_dir": "/mnt/md0/vods",
  "clip_dir": "/mnt/md0/clips"
}
```

`youtube-conf.json` - API json for [uploading videos to YouTube](https://developers.google.com/youtube/v3/guides/uploading_a_video).
```json
{
  "web": {
    "client_id": "[[INSERT CLIENT ID HERE]]",
    "client_secret": "[[INSERT CLIENT SECRET HERE]]",
    "redirect_uris": [],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

# License
This project is licensed under the zlib license, copyright Logan "NotQuiteApex" Hickok-Dickson. See LICENSE.md for more details.
