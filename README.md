# <img src="/assets/banner.png" alt="VodBot" height="100" /> [![GitHub license](https://badgen.net/github/license/NotQuiteApex/VodBot)](https://github.com/NotQuiteApex/VodBot/blob/master/LICENSE.md) [![PyPI version fury.io](https://badge.fury.io/py/vodbot.svg)](https://pypi.org/project/vodbot/) [![GitHub issues](https://img.shields.io/github/issues/NotQuiteApex/VodBot.svg)](https://gitHub.com/NotQuiteApex/VodBot/issues/)

VodBot is command line VOD and Clip manager for Twitch. Vodbot can:
* Grab info on any public VOD, Clip, or Channel on Twitch.
* Queue and download any available VOD or Clip from Twitch, along with useful metadata and chatlogs.
* Slice and splice videos downloaded in instances of staged data.
* Export instances one at a time or all at once, with chatlogs converted to common formats such as RealText or SAMI.
* Upload instances one at a time or all at once to YouTube, with chatlogs as captions/subtitles synced with the video.
	* NOTE: Requires approval and credentials from Google, for now just use export and upload manually.
* Bash tab completion, for quickly putting in commands.
    * NOTE: Available through argcomplete, see its repo for more details. Requires `eval "$(register-python-argcomplete vodbot)"` to be placed in an appropriate location such as `~/.bashrc` after installation.

...with more features to come!

# Installation
VodBot can be installed with `pip install vodbot`. You can also install by cloning the repo and running `pip install .` for the latest commits and changes, although this isn't recommended. This will not install FFmpeg or any of the optional dependencies, that must be done separately.

Dependencies/Requirements:
* [FFmpeg](https://ffmpeg.org/) (Must be in your PATH environment variable) ([recommended quick install](https://github.com/BtbN/FFmpeg-Builds))
* [Python 3.7+](https://www.python.org/)
    * [argcomplete](https://pypi.org/project/argcomplete/)
    * [dataclasses-json](https://pypi.org/project/dataclasses-json/)
    * [Requests](https://pypi.org/project/requests/)
    * [M3U8](https://pypi.org/project/m3u8/)
    * [Google API Client](https://pypi.org/project/google-api-python-client/)
    * [Google Auth OAuthLib](https://pypi.org/project/google-auth-oauthlib/)
    * [Google Auth httplib2](https://pypi.org/project/google-auth-httplib2/)
* Optionals:
    * For thumbnail generation: [ImageMagick](https://imagemagick.org/) (Must be in your PATH environment variable) ([recommended quick install](https://github.com/SoftCreatR/imei))

# Wiki
All documentation of VodBot and its usage is managed on the repo wiki, which can be found [here](https://github.com/NotQuiteApex/VodBot/wiki)! Please consult the wiki before contributing or opening issues.

## Project Status
VodBot is considered complete-enough. However, features will continue to be added and the project itself rewritten many times down the road for optimization and repo readability. Major changes should not be expected. Any future releases will be documented on the [projects page](https://github.com/NotQuiteApex/VodBot/projects).

# License and Credit
This project's code is licensed under the MIT license, copyright Logan "NotQuiteApex" Hickok-Dickson. See [LICENSE.md](LICENSE.md) for more details. All other assets such as but not limited to images or programs are owned and their use dictated by the asset's respective owner(s).

VodBot was built on the grounds laid by the streaming group Friend Team Inc. (for the original idea and necessity of the project), the many people who research Twitch's GraphQL API (for all the API calls that the project makes), and the support from friends and family (for, y'know, the support). Without any of this, VodBot would not exist as it currently does. 🧡
