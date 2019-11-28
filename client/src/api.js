import axios from 'axios';
import urljoin from 'url-join';
import * as environment from '../config/environment.json';

const api = axios.create({
    baseURL: '/api'
});
axios.defaults.headers.post['Content-Type'] = 'application/json';

export function url_for(parts) {
    if (!parts) {
        return '';
    }
    return urljoin(environment.vault, ...parts);
}

export default api;
