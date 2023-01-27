# v1.1.1 - Super Hotfix (January 21, 2023)
* Fixed an issue with the `vodbot init` command failing.
* Added `oauth_port` field to upload configuration section, for dictating what port the local OAuth server should use when logging into Google services.

# v1.1.0 - The Super Mega Super Overhaul (January 20, 2023)
### Major Additions/Changes:
- VodBot has changed licenses from zlib to MIT, in order to preserve crediting of work.
- VodBot now requires Python 3.7 or later, changed from requiring 3.6.
- New Python packages that have been added since last release: `argcomplete`, `dataclasses-json`, `pillow`.
- Config files have been completely reworked for internal use and better organization. The new default path to the config file is `~/.vodbot/config.json`. (#40)
- VodBot will now autocomplete arguments assuming the autocompletion setup is complete. (#24)
	- Requires `eval "$(register-python-argcomplete vodbot)"` to be placed in your `~/.bashrc`. 
	- Only fully compatible with Bash, with limited compatibility with other shells. See the [argcomplete page](https://pypi.org/project/argcomplete/) for more info.
- VodBot will now cache locally pulled videos and current stages to help with auto-complete. This cache is stored in the temp directory. If, for whatever reason, the cache gets desynced with what actually exists on the disk, it can be refreshed with the `-u` argument. (#55)
- VodBot can now generate, export, and upload thumbnails for videos. Details are entered during the staging process and can be enabled and configured with the config. See the wiki for details. (#42)
- VodBot can now push webhooks to Discord upon completion of certain tasks. See the wiki for details. (#35)

### Minor changes/fixes:
- VodBot will no longer continue to prompt for things that can be provided by arguments (such as streamers when staging), and exit when an argument does not match specific criteria.
- Vods, Clips, and Chat logs can now all be saved independently and per channel as defined in the config. Master toggles for each file can be set in the pull section of the config, disabling that download for every channel.
- Chat member names, when uncolored (white), can be made into a random color if enabled in the chat section of the config. (#40)
- Certain aspects of the YouTube Timed Text chat log export can be configured, such as position, anchoring, and alignment. (#40)
- Stage files can now be optionally left undeleted after export or upload, configurable in the stage section of the config. (#40)
- The amount of info displayed by FFmpeg (loglevel) can now be configured in the export section. Defaults to "warning". (#40)
- Logs from FFmpeg are now piped to `/dev/null` by default, but can be piped elsewhere with a configuration setting.
- Export can now selectively export chat logs, videos, and/or thumbnails (when available) with each using its own toggle in the export section of the config. All toggles default to on. (#40)
- Upload can now selectively upload chat logs and/or thumbnails (when available) with each using its own toggle in the upload section of the config. All toggles default to on.  (#40)
- Thumbnail generation has been added, along with its own section in the config as well as a new directory to be configured in the directories section. (#42)
- Stream chapters (moments when the stream changes games) are now saved and displayed where relevant. (#34)
- Users banned from Twitch that show up in chat logs will receive a fake username when detected. (#44)
- Videos would fail to concatenate when segments of the video were muted, this has been *potentially* fixed. (#51)
	- Note that this still does not bypass the mute itself, simply that the video will remain intact.
- Entity codes (specifically `<`, `>`, and `&`) for YouTube Timed Text have been fixed. (#48)
- Crashes related to permissions when creating directories has been fixed. (#50)
- Chat parsing no longer fails when chat log is empty. (#45)
- Video descriptions will no longer accept certain characters (`<` and `>`) due to issues when uploading to YouTube. (#46)
- Google OAuth session information is now saved as a JSON rather than pickled. (#49)
- VodBot will no longer crash when moving files across drives on Windows. (#52)
- Due to Google disabling of Out-Of-Band authentication with OAuth, VodBot now uses a local server method (via localhost:8080). (#60)
- Up to 1000 channels can be selected quickly by index rather than requiring full input when selecting channels for staging. (#41)
- Color output is disabled when stdout is routed to a non-tty output.

# v1.0.0 - Initial Release! (November 16, 2021)
VodBot is finally "finished"! This however will not be the final major release, there will be future versions with more features and fixes.

- Init command: `vodbot init`
	- Initializes directories and config files in default/user designated locations.
	- Running this is recommended prior to performing any other function.
- Pull/Download command: `vodbot pull [vods/clips/both]` or `vodbot download ...`
	- Pulls video data from Twitch based on channels listed in the config file.
	- Video data can be VODs, Clips, or both; by default both will be downloaded.
	- Chat logs are also downloaded for VODs if enabled in config (on by default).
- Stage command: `vodbot stage <subcommand>`
	- New stage: `vodbot stage new <video_id> [video_id ...]` Creates instance of staged data, specifically title, description, and video slices for use with exporting and uploading. Allows for multiple videos in one stage to be concatenated on export.
	- List stages: `vodbot stage list [stage_id]`, will either list all stages or specific info on staged instance provided an ID.
	- Remove stage: `vodbot stage rm <stage_id>`, removes a specific staged instance.
- Export command: `vodbot export <stage_id/all> <export_directory>`
	- Exports videos from staged instances. Individual videos or all can be exported to a specific directory.
	- Export directory will be created if non-existant.
	- Warning: exports with matching filenames will overwrite existing files.
- Upload/Push command: `vodbot upload <stage_id/all>` or `vodbot push ...`
	- Note: VodBot requires special files for YouTube uploading permission. These files are not included with this release and will not be given to random people, only those that I (Logan "NotQuiteApex" H-D) trust due to permissions issues with Google. This will likely change in a future release.
	- Uploads individual or all staged instances of video data.
	- Videos are exported identically to the export command into a temp directory (defined in config) before being uploaded.
	- Allows use of macros and runtime generated strings for descriptions, defined by VodBot or in config.
	- If not authorized, a link will appear asking for a special code. Open the link and allow VodBot access to manage your YouTube videos (worry not, this is *only* for uploading). When fully authorized, a string will appear that must be copied back into VodBot to continue.

# v0.9.9 - Test Pre-release. (October 22, 2021)
This is a test pre-release. VodBot is useable in this release, but incomplete and untested.

# 104b8fd - Initial commit. (November 16, 2020)
Happy Birthday, VodBot :)
