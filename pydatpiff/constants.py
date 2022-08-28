# base player state management keys
# see: pydatpiff.backend.audio.baseplayer.BasePlayer.state
player_state_keys = {
    "loaded": "loaded",
    "playing": "playing",
    "paused": "paused",
    "stopped": "stopped",
    "system_stopped": "system_stopped",
}

# base player state symbols
music_symbols = {
    "playing": chr(9199),  # |>
    "paused": chr(9208),  # ||
    "stopped": chr(9209),  # []
    "music": chr(9836),  # music note
    "autoplay": chr(9871),  # loop
}


# Html unicode characters
ampersands = [
    "&quot;",  # ""
    "&amp;",  # &
    "&lt;",  # <
    "&gt;",  # >
    "&nbsp;",  # space
    "&iexcl;",  # ¡
    "&cent;",  # ¢
    "&pound;",  # £
    "&curren;",  # ¤
    "&yen;",  # ¥
    "&brvbar;",  # ¦
    "&sect;",  # §
    "&uml;",  # ¨
    "&copy;",  # ©
    "&ordf;",  # ª
    "&laquo;",  # «
    "&not;",  # ¬
    "&shy;",  #
    "&reg;",  # ®
    "&macr;",  # ¯
    "&deg;",  # °
    "&plusmn;",  # ±
    "&sup2",  #
    "&sup3;",  # ³
    "&acute;",  # ´
    "&micro;",  # µ
    "&para;",  # ¶
    "&middot;",  # ·
    "&cedil;",  # ¸
    "&sup1;",  # ¹
    "&ordm;",  # º
    "&raquo;",  # »
    "&frac14;",  # ¼
    "&frac12;",  # ½
    "&frac34;",  # ¾
    "&iquest;",  # ¿
    "&times;",  # ×
    "&divide;",  # ÷
    "&ETH;",  # Ð
    "&eth;",  # ð
    "&THORN;",  # Þ
    "&thorn;",  # þ
    "&AElig;",  # Æ
    "&aelig;",  # æ
    "&OElig;",  # Ø
    "&oelig;",  # ø
    "&Aring;",  # Å
    "&Oslash;",  # Ø
    "&Ccedil;",  # Ç
    "&ccedil;",  # ç
    "&szlig;",  # ß
    "&Ntilde;",  # Ñ
    "&ntilde;",  # ñ
]

verbose_message = {
    "MEDIA_INITIALIZED": "Media initialized",
    "MEDIA_SET": "Setting media to %s",
    "MEDIA_NOT_SET": "Media not set... Please call `setMedia` first",
    "SEARCH_SONG": "Searching for song: %s ...",
    "NO_SONG_SELECTED": "--- No song was entered --",
    "SONG_NOT_FOUND": "No song was found",
    "SONG_NAME_NOT_FOUND": "No song was found with the name: %s",
    "UNAVAILABLE_SONG": "This song is unavailable",
    "INVALID_DIRECTORY": "Invalid directory: %s",
    "SAVE_SONG": "Saving song: %s ...",
    "SAVE_ALBUM": "Album saved: %s to %s",
    "AUTO_PLAY_NO_SONG": "Play a song first to enable autoplay",
    "AUTO_PLAY_NEXT_SONG": "Playing next song",
    "AUTO_PLAY_LAST_SONG": "No more songs left to autoplay",
    "AUTO_PLAY_ENABLED": "\t----- AUTO PLAY ON -----",
    "AUTO_PLAY_DISABLED": "\t----- AUTO PLAY OFF -----",
    "AUTO_PLAY_INACTIVITY": "\t--- Autoplay stopped due to inactivity ---",
}

SERVER_DOWN_MSG = (
    "\n\t--- UNOFFICIAL DATPIFF MESSAGE --"
    "\nSorry, we encounter a problem with our server!"
    " Please try again later."
)
