import api, { url_for } from '../api';

export default class Browser {

    filter = '';
    chapter = 1;
    lastChapter = 0;

    constructor() {
        this.covers = []
        this.url_for = url_for
    }

    activate(data) {
        const chapter = data.chapter ? Number(data.chapter) : 1;
        this.search(chapter);
    }

    async getGalleryCount() {
        const response = await api.post('count-galleries');
        this.lastChapter = Math.ceil(response.data.count / 9);
    }

    async requestCovers() {
        this.covers.splice(0, 9);
        const response = await api.post('covers', {
            'offset': (this.chapter - 1) * 9,
            'limit': 9
        })
        this.covers.push(...response.data)
    }

    changeChapter(forward) {
        if ((forward && this.chapter >= this.lastChapter)
            || (!forward && this.chapter <= 1)) {
            return;
        }
        this.chapter += forward ? +1 : -1;
        this.requestCovers();
    }

    async search(chapter) {
        //TODO search lol
        console.log('Searching: ' + this.filter);
        await this.getGalleryCount()
        this.chapter = chapter;
        this.requestCovers()
    }

    onPointerDown(e) {
        //TODO details on long click?
    }

    onPointerUp(e) {
        e.path.some((el) => {
            if (el.classList.contains('cover-container')) {
                const dir = el.getAttribute('dir')
                window.open(`#/gallery/${dir}`, '_blank');
                return true;
            }
        })
    }
}
