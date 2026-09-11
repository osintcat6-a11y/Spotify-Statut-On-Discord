
---

### `main.py`

```python
import time
import re
import requests

# ================== CONFIG ==================
DISCORD_TOKEN = "token"
DISCORD_USER_ID = "discordid"
PREFIX = "🎶 "
POLL_INTERVAL = 2.5
# ============================================

last_status = ""
current_lyrics = []
current_track_id = None


def get_spotify():
    try:
        r = requests.get(
            f"https://api.lanyard.rest/v1/users/{DISCORD_USER_ID}",
            timeout=5
        )
        data = r.json()

        if not data.get("success"):
            return None

        spotify = data["data"].get("spotify")
        if not spotify:
            return None

        return {
            "title": spotify["song"],
            "artist": spotify["artist"],
            "start": spotify["timestamps"]["start"] / 1000,
            "track_id": spotify["track_id"]
        }
    except Exception as e:
        print("Erreur Lanyard:", e)
        return None


def get_lyrics(artist: str, title: str):
    try:
        artist = artist.split(";")[0].strip()

        r = requests.get(
            "https://lrclib.net/api/get",
            params={"artist_name": artist, "track_name": title},
            timeout=5
        )

        if r.status_code != 200:
            r = requests.get(
                "https://lrclib.net/api/search",
                params={"artist_name": artist, "track_name": title},
                timeout=5
            )
            if r.status_code != 200 or not r.json():
                return []
            data = r.json()[0]
        else:
            data = r.json()

        synced = data.get("syncedLyrics")
        if not synced:
            return []

        lines = []
        for line in synced.splitlines():
            match = re.match(r"\[(\d+):(\d+\.\d+)\](.*)", line)
            if match:
                minutes, seconds, text = match.groups()
                timestamp = int(minutes) * 60 + float(seconds)
                lines.append((timestamp, text.strip()))

        return lines
    except Exception as e:
        print("Erreur lyrics:", e)
        return []


def set_status(text: str):
    global last_status

    if text == last_status:
        return

    headers = {
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "custom_status": {
            "text": text[:128],
            "expires_at": None,
            "emoji_id": None,
            "emoji_name": None
        }
    }

    try:
        r = requests.patch(
            "https://discord.com/api/v9/users/@me/settings",
            headers=headers,
            json=payload,
            timeout=5
        )
        if r.status_code == 200:
            last_status = text
            print("→", text)
        elif r.status_code == 429:
            print("Rate limit Discord, on attend un peu...")
            time.sleep(5)
        else:
            print("Erreur Discord:", r.status_code)
    except Exception as e:
        print("Erreur requête Discord:", e)


def main():
    global current_lyrics, current_track_id

    print("Lyrics Status (via Lanyard) lancé...\n")
    print("N'oublie pas : serveur Lanyard + Spotify en lecture + statut activé\n")

    while True:
        try:
            info = get_spotify()

            if not info:
                set_status("")
                time.sleep(POLL_INTERVAL)
                continue

            # Nouvelle musique
            if info["track_id"] != current_track_id:
                current_track_id = info["track_id"]
                print(f"\nNouvelle track : {info['artist']} - {info['title']}")
                current_lyrics = get_lyrics(info["artist"], info["title"])

                if not current_lyrics:
                    print("→ Pas de paroles trouvées")
                    set_status(f"{PREFIX}{info['title']} - {info['artist']}")
                    time.sleep(POLL_INTERVAL)
                    continue
                else:
                    print(f"→ {len(current_lyrics)} lignes de paroles chargées")

            # Position actuelle
            progress = time.time() - info["start"]

            current_line = ""
            for timestamp, text in current_lyrics:
                if timestamp <= progress:
                    current_line = text
                else:
                    break

            if current_line:
                set_status(f"{PREFIX}{current_line}")
            else:
                set_status(f"{PREFIX}{info['title']} - {info['artist']}")

        except Exception as e:
            print("Erreur générale:", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()