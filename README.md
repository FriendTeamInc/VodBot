# <img src="/assets/banner.png" alt="VodBot" height="100" />
[![GitHub license](https://badgen.net/github/license/FriendTeamInc/VodBot)](LICENSE.md) [![PyPI version fury.io](https://badge.fury.io/py/vodbot.svg)](https://pypi.org/project/vodbot/) [![GitHub issues](https://img.shields.io/github/issues/FriendTeamInc/VodBot.svg)](https://gitHub.com/FriendTeamInc/VodBot/issues/)

VodBot is command line VOD and Clip manager for Twitch. Vodbot can:
* Grab info on any public VOD, Clip, or Channel on Twitch.
* Download any public VOD or Clip from Twitch, along with useful metadata and chatlogs.
* Slice and splice videos downloaded into instances of staged data.
* Export staged data, one at a time or all at once, with chat logs as subtitles synced with the video and programmatically generated thumbnails.
* Upload staged data, one at a time or all at once, to YouTube with chat logs as subtitles synced with the video and programmatically generated thumbnails.
* Bash tab completion, for quickly putting in commands and referencing saved videos or staged data.
    * NOTE: Available through the argcomplete package, see its repo for more details. Requires `eval "$(register-python-argcomplete vodbot)"` to be placed in an appropriate location such as `~/.bashrc` after installation.
* Send webhooks to Discord to help you keep tabs on what VodBot is up to.

...with more features to come!

# Installation
VodBot can be installed with `pip install vodbot`. You can also install by cloning the repo and running `pip install .` for the latest commits and changes, although this isn't recommended. FFmpeg must be installed separately.

Dependencies/Requirements:
* [FFmpeg](https://ffmpeg.org/)
    * Must be in your PATH environment variable.
    * Latest builds available [here](https://github.com/BtbN/FFmpeg-Builds).
* [Python 3.7+](https://python.org/)
    * [argcomplete](https://pypi.org/project/argcomplete/)
    * [dataclasses-json](https://pypi.org/project/dataclasses-json/)
    * [Requests](https://pypi.org/project/requests/)
    * [M3U8](https://pypi.org/project/m3u8/)
    * [Google API Client](https://pypi.org/project/google-api-python-client/)
    * [Google Auth OAuthLib](https://pypi.org/project/google-auth-oauthlib/)
    * [Google Auth httplib2](https://pypi.org/project/google-auth-httplib2/)
    * [Pillow](https://pypi.org/project/Pillow/)

# Wiki
All documentation of VodBot and its usage is managed on the repo wiki, which can be found [here](https://github.com/FriendTeamInc/VodBot/wiki)! Please consult the wiki before contributing or opening issues.

# Project Status
VodBot is considered complete-enough. However, features will continue to be added and the project itself rewritten many times down the road for optimization and repo readability. Major changes to arguments and commands should not be expected. Any future releases will be documented on the [milestones page](https://github.com/FriendTeamInc/VodBot/milestones).

# License and Credit
This project's code is licensed under the MIT license, copyright Logan "NotQuiteApex" Hickok-Dickson. See [LICENSE.md](LICENSE.md) for more details. All other assets in this repository such as but not limited to images or programs are owned and their use dictated by the asset's respective owner(s).

VodBot was built on the grounds laid by the streaming group Friend Team Inc. (for the original idea and necessity of the project), the many people who research Twitch's GraphQL API (for all the API calls that the project makes), and the support from friends and family (for, y'know, the support). Without any of this, VodBot would not exist as it currently does. 🧡
