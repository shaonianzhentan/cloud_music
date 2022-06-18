import requests, uuid, time, json

class CloudMusic():

    def __init__(self, hass) -> None:
        self.hass = hass