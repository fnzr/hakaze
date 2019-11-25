import axios from 'axios';

const api = axios.create({
    baseURL: '/api'
});
axios.defaults.headers.post['Content-Type'] = 'application/json';

export function url_for(filepath) {
    return filepath ? '/vault/' + filepath : '';
}

export default api;
