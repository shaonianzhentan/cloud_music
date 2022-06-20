export function getHass() {
    const ha = parent.document.querySelector('home-assistant') as any
    return ha.hass
}
const hass = getHass()

export function cloudMusicServer(data: object) {
    hass.sendWS({ type: 'cloud_music_server', data })
}

export async function hassFetch(url: string, options = {}): Promise<any> {
    return await hass.fetchWithAuth(url, options).then((res: any) => res.json())
}

export async function cloudMusicApi(url: string, options = {}): Promise<any> {
    return await hassFetch(`/ha_cloud_music-api?api=${url}`, options)
}

export async function cloudMusicFetch(url: string, options = {}): Promise<any> {
    return await hassFetch(`/ha_cloud_music-api?api=${url}`, options)
}

export async function cloudMusicPost(data: object): Promise<any> {
    return await hassFetch('/ha_cloud_music-api', {
        method: 'POST',
        body: JSON.stringify(data)
    })
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

export interface ISong {
    id: number,
    name: string,
    singer: string,
    album: string,
    picUrl: string,
    duration: string
}