@echo off
setlocal enabledelayedexpansion
echo Searching for VideoForDelete...

set "found="
for %%e in (mp4 webm avi mkv mov) do (
    if exist "VideoForDelete.%%e" (
        set "input=VideoForDelete.%%e"
        set "ext=%%e"
        set "found=1"
        goto :process
    )
)

if not defined found (
    echo ERROR: VideoForDelete not found with supported extensions (mp4, webm, avi, mkv, mov)
    pause
    exit /b 1
)

:process
echo Found: %input%
echo Processing...

set "output=VideoForDelete_fixed.%ext%"

ffmpeg -fflags +genpts+igndts+discardcorrupt -err_detect ignore_err ^
    -i "%input%" ^
    -c:v libx264 -preset medium -crf 23 ^
    -c:a aac -b:a 128k ^
    -movflags +faststart ^
    "%output%"

if %errorlevel% neq 0 (
    echo ERROR: ffmpeg failed to process the video
    pause
    exit /b 1
)

echo Replacing original file...
del "%input%"
ren "%output%" "%input%"

echo Done! Video fixed and saved as: %input%
pause