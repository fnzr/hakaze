import api, { url_for } from '../api';
export default class Gallery {

    dir = '';
    pages = []
    firstPage = -9;

    activate(data) {
        this.dir = data.dir;
        this.requestPages(true)
        this.url_for = url_for
    }

    //TODO prevent forward after end
    //basically load gallery info and stuff
    async requestPages(forward) {
        if (!forward && this.firstPage == 0) {
            return;
        }
        this.firstPage += (forward ? +1 : -1) * 9;
        this.pages.splice(0, 9);
        const response = await api.post('pages', {
            'offset': this.firstPage,
            'limit': 9,
            'dir': this.dir
        })
        this.pages.push(...response.data)
    }
}
