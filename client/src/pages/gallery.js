import screenfull from 'screenfull';
import api, { url_for } from '../api';

export default class Gallery {

    dir = '';
    pages = {}
    shownPages = []
    chapter = 1;
    lastChapter = 0;
    fullscreenPage = 0;
    gallery = {
        length: 0
    }

    fullscreen = {
        close: () => screenfull.exit(),

        next: () => {
            if (this.gallery.length <= this.fullscreenPage) {
                return;
            }
            this.fullscreenPage++;
        },

        previous: () => {
            if (this.fullscreenPage == 1) {
                return;
            }
            this.fullscreenPage--;
        }
    }

    constructor() {
        screenfull.on('change', () => {
            if (!document.fullscreenElement) {
                this.showChapter(Math.ceil(this.fullscreenPage / 9))
                this.fullscreenPage = 0
            }
        })
    }


    activate(data, routeConfig) {
        this.dir = data.dir;
        this.requestGalleryData().then(async () => {
            routeConfig.navModel.setTitle(this.gallery.title)
            //TODO deal with gallery with over 50 pages
            await this.requestPages(0, 50)
            this.showChapter(1)
        })
        this.url_for = url_for
    }

    async requestGalleryData() {
        const response = await api.get(`gallery/${this.dir}`)
        this.gallery = response.data;
        this.lastChapter = Math.ceil(this.gallery.length / 9);
    }

    async requestPages(offset, limit) {
        if (this.lastLoadedPage >= this.gallery.length) {
            return
        }
        const response = await api.post('pages', {
            'offset': offset,
            'limit': limit,
            'dir': this.dir
        })
        this.lastLoadedPage = offset + limit;
        for (const key in response.data) {
            this.pages[Number(key)] = url_for(response.data[key]);
        }
    }

    showChapter(chapter) {
        this.chapter = chapter;
        const offset = (chapter - 1) * 9;
        this.shownPages.splice(0, 9);
        const limit = Math.min(9, this.gallery.length - offset)
        for (let i = 1; i <= limit; i++) {
            const key = i + offset;
            const value = (key in this.pages) ? this.pages[key] : ''
            this.shownPages.push({
                'num': key,
                'url': value
            });
        }
    }

    changeChapter(forward) {
        if ((forward && this.chapter >= this.lastChapter)
            || (!forward && this.chapter < 1)) {
            return;
        }
        const nextChapter = this.chapter + (forward ? +1 : -1);
        this.showChapter(nextChapter);
    }

    onPointerUp(e) {
        e.path.some(el => {
            if (el.classList.contains('cover-container')) {
                const pageNumber = el.getAttribute('data-page')
                this.fullscreenPage = Number(pageNumber);
                screenfull.request(document.getElementById('fullscreen'));
                return true;
            }
        })
    }
}
