import os

from Constants import MAX_VIDEO_DOWNLOAD_SIZE
from src.downloader import DownloadedVideos, AlternateVideoDownloader


class YoutubeDownloader(AlternateVideoDownloader):
    @classmethod
    async def download_video_from_link(
        cls, url: str, path: str | None = None
    ) -> DownloadedVideos:
        if path is None:
            path = os.path.join("downloads", "youtube")

        os.makedirs(path, exist_ok=True)

        costum_options = {
            "format": f"bestvideo[filesize<{MAX_VIDEO_DOWNLOAD_SIZE}M][ext=mp4]+bestaudio[ext=m4a]/best[filesize<{MAX_VIDEO_DOWNLOAD_SIZE}M][ext=mp4]",
            "outtmpl": os.path.join(path, "%(id)s.mp4"),
            "noplaylist": True,
            "default_search": "auto",
            "nooverwrites": True,
            "quiet": True,
        }

        return await cls._get_list_from_ydt(url, path, ydl_opts=costum_options)
