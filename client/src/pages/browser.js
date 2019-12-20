import api from '../api';

export default class Browser {

    filter = '';
    downloadURL = '';
    chapter = 1;
    lastChapter = 0;
    randomMode = false;

    constructor() {
        this.covers = []
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
        let response;
        const args = { 'limit': 9 };
        if (this.randomMode) {
            args['random'] = true;
        }
        else {
            args['skip'] = (this.chapter - 1) * 9;
        }
        response = await api.post('covers', args)
        this.covers.push(...(response.data.map(cover => {
            cover['url'] = `/thumb/300,fit/${cover.path}`
            return cover;
        })))
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

    async download() {
        const response = await api.post('download-gallery', {
            url: this.downloadURL
        });
        console.log(response)
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
