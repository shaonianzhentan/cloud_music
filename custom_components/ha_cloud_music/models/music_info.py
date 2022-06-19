

class MusicInfo:

    def __init__(self, id, song, singer, album, duration, url, picUrl) -> None:
        self._id = id
        self._song = song
        self._singer = singer
        self._duration = duration
        self._album = album
        self._url = url
        self._picUrl = picUrl

    @property
    def song(self):
        return self._song

    @property
    def singer(self):
        return self._singer

    @property
    def album(self):
        return self._album

    @property
    def url(self):
        return self._url

    @property
    def picUrl(self):
        return self._picUrl