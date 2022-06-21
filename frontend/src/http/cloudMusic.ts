
import _ from 'lodash'
export class HA {

    SERVER = 'cloud_music_server'
    CLIENT = 'cloud_music_client'
    hass = this.homeassistant.hass
    audio = new Audio()
    entity_id = ''
    attrs = {
        album: '',
        artist: '',
        image: '',
        title: '',
    }

    constructor() {
        this.audio.muted = false
        this.cloudMusicServer({ action: 'init' }).then((data) => {
            this.attrs.album = data.media_album_name
            this.attrs.artist = data.media_artist
            this.attrs.title = data.media_title
            this.attrs.image = data.media_image_url
            // console.log(this.audio)
            this.entity_id = data.entity_id
            if (data.media_content_id) this.audio.src = data.media_content_id
        })
        this.audio.ontimeupdate = _.throttle(this.onupdate.bind(this), 1000)
        this.audio.onended = this.onended.bind(this)
        // 订阅事件
        this.subscribeEvents(({ data }: any) => {
            console.log(data)
            const { audio } = this
            // 加载音乐
            if ('play_media' in data) {
                this.attrs.album = data.media_album_name
                this.attrs.artist = data.media_artist
                this.attrs.title = data.media_title
                this.attrs.image = data.media_image_url
                audio.src = data.play_media
                audio.play()
                return
            }
            // 操作
            if ('action' in data) {
                switch (data.action) {
                    case 'play':
                        if (audio.paused) audio.play()
                        break;
                    case 'pause':
                        if (!audio.paused) audio.pause()
                        break;
                }
            }
            // 设置音量
            if ('volume_level' in data) {
                audio.volume = data.volume_level
            }
            // 静音
            if ('is_volume_muted' in data) {
                audio.muted = data.is_volume_muted
            }
            // 进度
            if ('media_position' in data) {
                audio.currentTime = data.media_position
            }
        })

    }

    onupdate() {
        const { audio } = this
        console.log(audio.currentTime)
        // 更新
        this.cloudMusicServer({
            action: 'update',
            media_position: audio.currentTime,
            media_duration: audio.duration,
            volume_level: audio.volume,
            is_volume_muted: audio.muted
        })
    }

    onended() {
        console.log('结束啦')
        this.next()
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
        return await this.hass.callWS({ type: 'cloud_music_server', data })
    }

    subscribeEvents(callback: Function) {
        console.log('订阅事件')
        this.hass.connection.subscribeEvents(callback, this.CLIENT)
    }

    fire(type: string, data = {}) {
        const event: any = new parent.window.Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = data;
        this.homeassistant.dispatchEvent(event);
    }

    // 上一曲
    previous() {
        const { entity_id } = this
        this.hass.callService('media_player', 'media_previous_track', { entity_id })
    }
    // 下一曲
    next() {
        const { entity_id } = this
        this.hass.callService('media_player', 'media_next_track', { entity_id })
    }
    // 播放
    play() {
        console.log(this.audio)
        this.audio.play()
        const { entity_id } = this
        this.hass.callService('media_player', 'media_play', { entity_id })
    }
    // 暂停
    pause() {
        console.log(this.audio)
        this.audio.pause()
        const { entity_id } = this
        this.hass.callService('media_player', 'media_pause', { entity_id })
    }
}

export const ha = new HA()

// 解决音乐播放问题
document.onmousemove = () => {
    ha.audio.muted = false
    document.onmousemove = null
    console.log('删除事件')
}

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
