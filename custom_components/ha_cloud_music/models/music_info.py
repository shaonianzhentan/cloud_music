import enum

class MusicSource(enum.Enum):

    URL = 1
    PLAYLIST = 2
    DJRADIO = 3
    XIMALAYA = 4


class MusicInfo:

    def __init__(self, id, song, singer, album, duration, url, picUrl, source) -> None:
        self._id = id
        self._song = song
        self._singer = singer
        self._duration = duration
        self._album = album
        self._url = url
        self._picUrl = picUrl
        self._source = source

    @property
    def id(self):
        return self._id

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

    @property
    def source(self) -> MusicSource:
        return self._source