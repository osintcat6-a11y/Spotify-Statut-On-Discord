# Discord Lyrics Status

Python script that updates your Discord custom status with synchronized lyrics from the song currently playing on Spotify.

It reads your Spotify activity through Lanyard (no Spotify API keys required).

## Features

- Real-time synchronized lyrics
- Uses Lanyard (no Spotify Client ID / Secret needed)
- Basic Discord rate-limit handling
- Fallback to track title + artist when lyrics are unavailable
- Lightweight and simple

## Disclaimer

This script uses a Discord **user token** to update your custom status.

This violates Discord's Terms of Service (self-botting / user automation).  
Use at your own risk. Account bans are possible.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/osintcat6-a11y/discord-lyrics-status.git
cd discord-lyrics-status
