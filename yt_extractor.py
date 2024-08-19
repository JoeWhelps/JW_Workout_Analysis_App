import yt_dlp
from yt_dlp.utils import DownloadError

ydl = yt_dlp.YoutubeDL()


def get_info(url):
    with ydl:
        try:
            result = ydl.extract_info(
                url,
                download=False
            )
        except DownloadError:
            return None
        
    if "entries" in result:
        video = result["entries"][0]
    else:
        video = result
        
    infos = ['id', 'title', 'channel', 'view_count', 'like_count',
             'channel_id', 'duration', 'categories', 'tags']
    def key_name(key):
        if key == "id":
            return "video_id"
        return key
    
    return {key_name(key): video[key] for key in infos}
