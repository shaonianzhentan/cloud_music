export class HA {

    SERVER = 'cloud_music_server'
    CLIENT = 'cloud_music_client'
    hass = this.homeassistant.hass
    audio = new Audio()
    entity_id = ''

    constructor() {
        this.audio.muted = false
        ha.cloudMusicServer({ action: 'init' }).then((data) => {
            console.log(this.audio)
            this.entity_id = data.entity_id
            this.audio.src = data.media_content_id
        })
    }

    get homeassistant(): any {
        return parent.document.querySelector('home-assistant')
    }

    async fetchWithAuth(url: string, options = {}): Promise<any> {
        return await this.hass.fetchWithAuth(url, options).then((res: any) => res.json())
    }

    async neteaseCloudMusic(url: string) {
        return await this.fetchWithAuth(`/ha_cloud_music-api?api=${url}`)
    }

    async cloudMusicApi(data: object) {
        return await this.fetchWithAuth('/ha_cloud_music-api', {
            method: 'POST',
            body: JSON.stringify(data)
        })
    }

    async cloudMusicServer(data: object): Promise<any> {
        return await this.hass.sendWS({ type: 'cloud_music_server', data })
    }

    subscribeEvents(callback: Function) {
        console.log('订阅事件')
        this.hass.connection.subscribeEvents(callback, ha.CLIENT)
    }

    // 上一曲
    previous() {

    }
    // 下一曲
    next() {

    }
    // 播放
    play() {
        this.audio.play()
    }
    // 暂停
    pause() {
        this.audio.pause()
    }
}

export const ha = new HA()

// 推荐
export interface IPersonalized {
    id: number,
    name: string,
    picUrl: string,
}

// toplist
export interface IToplist {
    id: number,
    name: string,
    description: string,
    coverImgUrl: string,
    updateFrequency: string,
}

// 歌手
export interface IArtists {
    id: number,
    name: string,
    picUrl: string,
}

// 音乐
export interface ISong {
    id: number,
    name: string,
    singer: string,
    album: string,
    picUrl: string,
    duration: string
}
