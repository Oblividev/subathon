# Social media assets for Obliviosa

## What was automated

**Twitch** (`twitch.tv/obliviosaofficial`) — profile, channel banner, and 8 recent clip thumbnails are in `img/pictures/` as:

- `LivTwitchProfile.png`, `LivTwitchBanner.png`
- `LivClip01.png` … `LivClip08.png`

Map events use **Show Picture** when the player examines posters (see `tools/add_social_photo_events.py`).

**Instagram** — automated download failed: `instagram.com/obliviosaofficial` returned “user not found” for gallery-dl. Use the exact handle Liv uses on Instagram.

## Adding Instagram photos manually

1. Export posts as PNG/JPG (or save from the app).
2. Copy into `img/pictures/` with clear names, e.g. `LivInsta01.png`.
3. In RPG Maker MZ, duplicate any “social photo” event and change the **Show Picture** filename and dialogue.

Or re-run gallery-dl once you have the correct URL:

```bash
python3 -m gallery_dl --range 1-12 -d img/pictures "https://www.instagram.com/YOUR_HANDLE_HERE/"
```

Rename downloads to `LivInsta01.png`, etc., then add events with `python3 tools/add_social_photo_events.py` (extend `MAP_PHOTOS` in that script).

## Video clips in-game

RPG Maker MZ does not play Twitch/Instagram video natively in **Show Picture**. Clip thumbnails stand in as “posters”; the theatre show event can open a URL via VisuMZ **Open URL** if you want real playback in a browser.

## Re-fetch Twitch thumbnails

```bash
curl -s -X POST 'https://gql.twitch.tv/gql' \
  -H 'Client-ID: kimne78kx3ncx6brgo4mv6wki5h1ko' \
  -H 'Content-Type: application/json' \
  -d '{"query":"query{user(login:\"obliviosaofficial\"){profileImageURL(width:600) bannerImageURL clips(first:8){edges{node{thumbnailURL}}}}}"}'
```

Download URLs from the JSON response into `img/pictures/`.
