import api from '../api';

export default class Browser {

    firstCover = -9

    constructor() {
        this.covers = []
        this.requestCovers(true)
    }

    async requestCovers(forward) {
        if (!forward && this.firstCover == 0) {
            return;
        }
        this.covers.splice(0, 9);
        console.log(this.covers.length)
        this.firstCover += (forward ? +1 : -1) * 9;
        const response = await api.post('covers', {
            'offset': this.firstCover,
            'limit': 9
        })
        this.covers.push(...response.data)
    }

    url_for(filepath) {
        return filepath ? '/vault/' + filepath : '';
    }

    onPointerDown(e) {
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
