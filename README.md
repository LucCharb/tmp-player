# tmp-player
Terminal Media Player
TMP - Terminal Media Player

A lightweight, customizable terminal-based media player built with Python. Supports audio and video playback with playlist management.
Features

    🎵 Audio playback (MP3, FLAC, WavPack, DSF)
    🎬 Video playback
    🗄️ SQLite database for media library
    ⚡ Fast and lightweight

Quick Start

For X11: (Note: Run xhost +local:docker first for X11 permissions.) docker run -it --rm
-v /your/media/path:/media:ro
-v ~/.tmp_data:/app/data
-v /run/user/$(id -u)/pulse:/run/user/1000/pulse
-e PULSE_SERVER=unix:/run/user/1000/pulse/native
--device /dev/dri
-e DISPLAY=$DISPLAY
-v /tmp/.X11-unix:/tmp/.X11-unix
kremata/tmp-player

For Audio Only (no video, works everywhere): docker run -it --rm
-v /your/media/path:/media:ro
-v ~/.tmp_data:/app/data
-v /run/user/$(id -u)/pulse:/run/user/1000/pulse
-e PULSE_SERVER=unix:/run/user/1000/pulse/native
kremata/tmp-player

For Wayland docker run -it --rm
-v /your/media/path:/media:ro
-v ~/.tmp_data:/app/data
-v /run/user/$(id -u)/pulse:/run/user/1000/pulse
-e PULSE_SERVER=unix:/run/user/1000/pulse/native
--device /dev/dri
-e XDG_RUNTIME_DIR=/tmp
-e WAYLAND_DISPLAY=$WAYLAND_DISPLAY
-v $XDG_RUNTIME_DIR/$WAYLAND_DISPLAY:/tmp/$WAYLAND_DISPLAY
kremata/tmp-player

Instruction: replace /your/media/path and use /media/[your-path-here] in the player. E.g. /mnt/media/music ==> /media/music

Remove ":ro" after /media if you wish TMP to save the lyrics on the drives.

How to use:

    You need to go in Settings and enter the source path of your audio/video.
    Scan the library to fill the DB.
