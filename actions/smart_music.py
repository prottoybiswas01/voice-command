r"""
Smart Music Dispatcher Module for Motu Assistant (Phase 2 & Phase 6 Upgrade).
Executes smart music playback routing strictly inside Google Chrome:
1. Spotify Web/App -> 2. YouTube Music -> 3. Local Music Folder.
"""

import os
import glob
import subprocess
import urllib.parse
from pathlib import Path
from typing import List, Optional
from config.settings import settings
from core.logger import logger
from core.database import db
from actions.system_actions import open_in_chrome


class SmartMusicDispatcher:
    """Manages priority-driven music playback strictly in Google Chrome."""

    def __init__(self) -> None:
        self.priority_list = settings.music.priority
        self.local_music_dir = settings.music.local_music_dir

    def play_music(self, query: str = "") -> str:
        """
        Smart music playback dispatcher.
        Automatically evaluates available sources in priority order.
        
        Args:
            query: Song name, artist, or empty string for default music.
            
        Returns:
            Status response string describing source chosen.
        """
        clean_query = query.strip()
        
        # Check user favorite music preference if query is empty
        if not clean_query:
            fav = db.get_user_preference("favorite_song") or db.get_user_preference("favorite_artist")
            if fav:
                clean_query = fav

        logger.info(f"Smart Music request for: '{clean_query or 'Default Music'}'")

        for source in self.priority_list:
            if source == "spotify":
                res = self._try_spotify(clean_query)
                if res:
                    db.log_command("smart_music:spotify", "SUCCESS", res)
                    return res

            elif source == "youtube":
                res = self._try_youtube(clean_query)
                if res:
                    db.log_command("smart_music:youtube", "SUCCESS", res)
                    return res

            elif source == "local":
                res = self._try_local_music(clean_query)
                if res:
                    db.log_command("smart_music:local", "SUCCESS", res)
                    return res

        # Ultimate fallback to YouTube in Google Chrome
        return self._try_youtube(clean_query or "relaxing music")

    def _try_spotify(self, query: str) -> Optional[str]:
        """Attempt Spotify web search specifically inside Google Chrome."""
        try:
            if query:
                encoded = urllib.parse.quote(query)
                spotify_url = f"https://open.spotify.com/search/{encoded}"
            else:
                spotify_url = "https://open.spotify.com"

            open_in_chrome(spotify_url)
            msg = f"Playing '{query or 'music'}' on Spotify in Google Chrome."
            logger.info(msg)
            return msg
        except Exception as err:
            logger.debug(f"Spotify attempt failed: {err}")
            return None

    def _try_youtube(self, query: str) -> str:
        """Play music via YouTube Search in Google Chrome."""
        search_query = f"{query} song" if query else "top hits music"
        encoded = urllib.parse.quote(search_query)
        yt_url = f"https://www.youtube.com/results?search_query={encoded}"
        open_in_chrome(yt_url)
        msg = f"Playing '{query or 'music'}' on YouTube in Google Chrome."
        logger.info(msg)
        return msg

    def _try_local_music(self, query: str) -> Optional[str]:
        """Scan local Music folder for audio files."""
        if not self.local_music_dir.exists():
            return None

        audio_extensions = ["*.mp3", "*.wav", "*.flac", "*.m4a"]
        audio_files: List[Path] = []

        for ext in audio_extensions:
            audio_files.extend(list(self.local_music_dir.glob(f"**/{ext}")))

        if not audio_files:
            return None

        target_file = audio_files[0]
        if query:
            for f in audio_files:
                if query.lower() in f.name.lower():
                    target_file = f
                    break

        try:
            os.startfile(str(target_file))
            msg = f"Playing local track: '{target_file.name}'."
            logger.info(msg)
            return msg
        except Exception as err:
            logger.debug(f"Failed to play local music file: {err}")
            return None


# Global Smart Music Dispatcher instance
smart_music_dispatcher = SmartMusicDispatcher()
