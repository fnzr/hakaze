import api, { url_for } from '../api';

export default class Browser {

    firstCover = -9
    galleryCount = 0;
    filter = '';

    constructor() {
        this.covers = []
        this.requestCovers(true)
        this.getGalleryCount()
        this.url_for = url_for
    }

    async getGalleryCount() {
        const response = await api.post('count-galleries');
        this.galleryCount = response.data.count;
    }

    async requestCovers(forward) {
        if (!forward && this.firstCover == 0 ||
            forward && this.firstCover >= this.galleryCount) {
            return;
        }
        this.firstCover += (forward ? +1 : -1) * 9;
        this.covers.splice(0, 9);
        const response = await api.post('covers', {
            'offset': this.firstCover,
            'limit': 9
        })
        this.covers.push(...response.data)
    }

    search() {
        //TODO search lol
        console.log('Searching: ' + this.filter);
    }

    onPointerDown(e) {
        //TODO details on long click?
    }

    onPointerUp(e) {
        e.path.some((el) => {
            if (el.classList.contains('cover-container')) {
                const dir = el.getAttribute('dir')
                console.log("Found: " + dir);
                return true;
            }
        })
    }
}
