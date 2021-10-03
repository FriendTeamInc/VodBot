# <img src="/assets/banner.png" alt="VodBot" height="100" /> by NotQuiteApex
A command line interface VOD and Clip manager for Twitch. Downloads VODs and Clips with appropriate metadata for any public channel, and allows for slicing and reupload to YouTube.

## Project Status
This project is a heavy **Work-In-Progress** project, and lots of changes can occur before an inevitable "release". This project is largely for my own uses and needs, and general usage isn't a major consideration in design, please keep this in mind before using. For progress and roadmap, check the [projects page](https://github.com/NotQuiteApex/VodBot/projects).

# Installation
Dependencies/Requirements:
* [Python 3.6+](https://www.python.org/)
    * [Requests 2.20+](https://pypi.org/project/requests/)
    * [M3U8 0.8+](https://pypi.org/project/m3u8/)
    * [Google API Client 2.0+](https://pypi.org/project/google-api-python-client/)
    * [Google Auth OAuthLib 0.4.4](https://pypi.org/project/google-auth-oauthlib/)
    * [Google Auth httplib2 0.1.0](https://pypi.org/project/google-auth-httplib2/)
* [ffmpeg](https://www.ffmpeg.org/) (Must be in your PATH environment variable)

VodBot can be installed with `pip install .`.

The Makefile in the repo simply invokes `pip` to uninstall previous versions of VodBot and install the latest changes, and currently should not be used to install VodBot.

# Wiki
All documentation of VodBot is managed on the repo wiki, which can be found [here](https://github.com/NotQuiteApex/VodBot/wiki)! The wiki is incomplete and will change lots while VodBot is developed.

# License
This project is licensed under the zlib license, copyright Logan "NotQuiteApex" Hickok-Dickson. See LICENSE.md for more details.
