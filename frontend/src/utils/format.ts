

export function formatPicUrl(url: string) {
    return `${url}?param=200y200`
}

export function formatDuration(duration: number) {
    const arr = (duration / 1000 / 60).toFixed(2).split('.')
    let m = arr[0]
    if (parseInt(m) < 10) m = `0${m}`
    return `${m}:${arr[1]}`
}