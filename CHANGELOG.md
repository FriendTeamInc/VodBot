# v1.1.0
### Released ???
TODO: write this.

# v1.0.0
### Released November 16, 2021
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

# v0.9.9 - Test Pre-release.
### Released October 22, 2021
This is a test pre-release. VodBot is useable in this release, but incomplete and untested.

# 104b8fd - Initial commit.
### Released November 16, 2020
Happy Birthday, VodBot :)
