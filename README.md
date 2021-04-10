# <img src="/assets/banner.png" alt="VodBot" height="100" /> by NotQuiteApex & FTI.
A VOD and clip manager for Twitch. Downloads VODs and clips with appropriate metadata for any public channel.

## Project Status
This project is a heavy Work-In-Progress, and lots of changes can occur before an inevitable "release". This project is largely for my own uses and needs, and general usage isn't a major consideration in design, please keep this in mind before using. For progress and roadmap, check the [projects page](https://github.com/NotQuiteApex/VodBot/projects).

# Installation
Requirements:
* [Python 3.6+](https://www.python.org/)
    * [Requests 2.20+](https://pypi.org/project/requests/)
    * [M3U8 0.8+](https://pypi.org/project/m3u8/)
    * [pytz 2021.1+](https://pypi.org/project/pytz/)
    * [Google API Client 2.0+](https://pypi.org/project/google-api-python-client/)
    * [Google Auth OAuthLib 0.4.4](https://pypi.org/project/google-auth-oauthlib/)
    * [Google Auth httplib2 0.1.0](https://pypi.org/project/google-auth-httplib2/)
* [ffmpeg](https://www.ffmpeg.org/) (Must be in your PATH)

VodBot can be installed with `pip install .`.

The Makefile in the repo simply invokes `pip` to uninstall previous versions of VodBot and install the latest changes, and currently should not be used to install VodBot.

# Usage
This section will best describe how to use VodBot, however you can always pull up a quick reference with `vodbot -h` or `vodbot <command> -h` on specific functionality.

* `vodbot init`: If it hasn't been run before, simply run `vodbot init` to initialize directories and files. Navigate to the path presented and edit the config accordingly. You can use the provided example config below as reference on how to set up VodBot.
* `vodbot pull`: This is the downloading functionality of VodBot, which will pull VODs or Clips onto a local drive. Running `vodbot pull vods` or `vodbot pull clips` will download the VODs or Clips of the channels you have set to watch in your config file, as well as some useful metadata into JSON files. Metadata JSON files contain the date (in UTC time), the user that streamed, the title, and the video ID. Clips metadata have all that info in addition to clip author and view count. Running `vodbot pull list [channel]` will list the data available locally of all the VODs and Clips of all channels or any specified channel, sorted chronologically.
* `vodbot stage`: This is the staging functionality of VodBot, making it easy to upload sections of VODs or Clips to YouTube. Running `vodbot stage add <video_id>` will begin the process of staging a VOD or Clip, found by the ID given in the command. You will get prompts for a video title, description, and start and stop times of the video (which defaults to the beginning and end of the video file), as well as who was streaming with the main streamer (entered as comma separated values). You can also avoid the prompts by passing arguments This will print out the data staged, as well as a stage ID. This can be used with the rest of the stage commands. Running `vodbot stage list [stage_id]` will print out all of the current stages, or provided a stage ID will print out info on that specific stage. Running `vodbot stage edit <stage_id>` will allow you to edit an existing stage. This will change the stage ID, so keep that in mind. Running `vodbot stage rm <stage_id>` will remove that specific stage.
* `vodbot upload`: This is the uploading functionality of VodBot, uploading staged data to a YouTube channel. Simply running `vodbot upload <stage_id>` will begin the uploading process for VodBot (you can also pass "all" in place of an ID to upload all stages). VodBot will load the stage(s), and then require authentication from a Google Account to upload videos to YouTube. VodBot will print a link that the user must open and authenticate the application with, then paste a unique code into a prompt from VodBot given by Google after authorizing VodBot. From there VodBot will attempt to upload the staged data to YouTube with all appropriate fields filled.
    *You will need to set the video to be public manually, as Google does not allow unapproved applications to upload public videos.*
    * YouTube brand channels cannot use anything other than the desktop website to upload videos, this includes the public API (and by extension VodBot.)

It's recommended that if you plan to use this for the long term to save the videos in some kind of redundant storage array or in multiple locations (or both). It's also recommended that VodBot is run with some kind of scheduling program like `systemd` or `cron` every so often to pull the VODs and clips for you.

# Configuration
Due to the nature of VodBot, application with Twitch and Google must be registered by the end user. While not ideal, this is the best and most secure solution that VodBot can currently use without compromising anything. This means certain functionality may be limited, such as the number of videos allowed to be uploaded in a given day, or how fast responses may come from endpoints.

### `conf.json` - Example config file. This is the one I use to manage my own VODs/Clips.
```json
{
  "twitch_channels": [ "46moura",
    "alkana", "batkigu", "hylianswordsman1"
    "juicibit", "michiri9", "notquiteapex",
    "pissyellowcrocs", "percy_creates", "voobo",
  ],

  "twitch_client_id": "[[INSERT CLIENT ID HERE]]",
  "twitch_client_secret": "[[INSERT CLIENT SECRET HERE]]",

  "stage_timezone": "US/Eastern",
  "stage_format": {
    "watch": "-- Watch live at {links}",
    "discord": "-- Join the Discord https://discord.gg/v2t6uag",
    "credits": "\n{watch}\n{discord}"
  },

  "youtube_client_path": "/root/.vodbot/yt-client.json",
  "youtube_pickle_path": "/root/.vodbot/yt-api-keys.pkl",

  "vod_dir": "/mnt/md0/vods",
  "clip_dir": "/mnt/md0/clips",
  "temp_dir": "/root/.vodbot/temp",
  "stage_dir": "/root/.vodbot/stage",
}
```

* `twitch_channels`: names of channels on twitch to pull VODs and clips from.
* `twitch_client_id`: ID string of client app, you must register your own with Twitch [here](https://dev.twitch.tv/console/apps).
* `twitch_client_secret`: Secret string of client app, you must register your own with Twitch [here](https://dev.twitch.tv/console/apps).
* `stage_timezone`: Timezone of the VODs/Clips, used for description formatting. Must be a useable string from the [pytz](http://pytz.sourceforge.net/) library.
* `stage_format`: A dictionary of strings that can be formatted with special predefined strings, or other strings from the dictionary. The predefined strings are described below.
    * `date`: The date the stream started, formatted as year/month/day.
    * `streamer`: The streamer who the video is of.
    * `streamers`: A list of all the streamers in the video, created when staged.
    * `link`: The link to the twitch of the `streamer`.
    * `links`: A space separated string of all the links of the streamers, created when staged.
* Below are files specific to the `vodbot upload` use case. These are specific to a Google Cloud App, you must register your own with Google with the "YouTube Data v3" API, *these should be stored in a secure place.*
    * `youtube_client_path`: Full path to the Client OAuth 2.0 JSON.
    * `youtube_pickle_path`: Full path to where VodBot should store it's session data.
* `vod_dir`: Full path to where VOD files are stored. This should be a safe place!
* `clip_dir`: Full path to where Clip files are stored. This should be a safe place!
* `temp_dir`: Full path to where VodBot will store sections of video to either download or upload. It is recommended this path is on a fast-to-write-to storage device.
* `stage_dir`: Full path to where VodBot will store text files of StageData, for use in uploading videos.

# License
This project is licensed under the zlib license, copyright Logan "NotQuiteApex" Hickok-Dickson. See LICENSE.md for more details.
