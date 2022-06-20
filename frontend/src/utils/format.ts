

export function formatPicUrl(url: string) {
    return `${url}?param=200y200`
}

export function formatDuration(duration: number) {
    const arr = (duration / 1000 / 60).toFixed(2).split('.')
    let m = arr[0]
    if (parseInt(m) < 10) m = `0${m}`
    return `${m}:${arr[1]}`
}

export function formatTime(seconds: number) {
    let result = Math.ceil(seconds)
    let h = Math.floor(result / 3600) < 10 ? '0' + Math.floor(result / 3600) : Math.floor(result / 3600);
    let m = Math.floor((result / 60 % 60)) < 10 ? '0' + Math.floor((result / 60 % 60)) : Math.floor((result / 60 % 60));
    let s = Math.floor((result % 60)) < 10 ? '0' + Math.floor((result % 60)) : Math.floor((result % 60));
    if (h === '00') return `${m}:${s}`
    return `${h}:${m}:${s}`
}