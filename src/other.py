import os
from src.downloader import DownloadedVideos, AlternateVideoDownloader


class UnknownAlternateDownloader(AlternateVideoDownloader):
    @classmethod
    async def download_video_from_link(
        cls, url: str, path: str | None = None
    ) -> DownloadedVideos:
        if path is None:
            path = os.path.join("downloads", "other")

        os.makedirs(path, exist_ok=True)

        ydt_opts = {
            "noplaylist": True,
            "default_search": "auto",
            "nooverwrites": False,  # We may have a video with the same id from a different source
        }

        return await cls._get_list_from_ydt(url, path, ydl_opts=ydt_opts)
