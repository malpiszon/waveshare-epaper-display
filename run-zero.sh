
. env.sh

function log {
    echo "---------------------------------------"
    echo ${1^^}
    echo "---------------------------------------"
}

if [ $WAVESHARE_EPD75_VERSION = 1 ]; then
    export WAVESHARE_WIDTH=640
    export WAVESHARE_HEIGHT=384
else
    export WAVESHARE_WIDTH=800
    export WAVESHARE_HEIGHT=480
fi

# Every step still runs (a failed fetch leaves the previous SVG, which is
# shown again), but any failure makes the script exit non-zero.
status=0

if [ $PRIVACY_MODE = 1 ]; then
    log "Get XKCD comic strip"
    .venv/bin/python3 xkcd_get.py || status=$?
    if [ $status -eq 0 ]; then
        .venv/bin/python3 display.py xkcd-comic-strip.png || status=$?
    fi

else

    log "Add weather info"
    .venv/bin/python3 screen-weather-get.py || status=$?

    # lnetatmo rewrites the token file on rotation; flush it now so a power
    # loss can't bring back an already-revoked refresh token.
    if [ -f ~/.netatmo.credentials ]; then
        sync ~/.netatmo.credentials
    fi

    log "Export to PNG"
    # -u: CairoSVG >= 2.6 refuses to load the icon files without it
    .venv/bin/cairosvg -u -o screen-output.png -f png --dpi 300 --output-width $WAVESHARE_WIDTH --output-height $WAVESHARE_HEIGHT screen-output-weather.svg || status=$?


    .venv/bin/python3 display.py screen-output.png || status=$?
fi

exit $status
