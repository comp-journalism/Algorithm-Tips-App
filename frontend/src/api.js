let HOST = "";
if (process.env.NODE_ENV !== 'production') {
    HOST = "http://localhost:8080";
}
const BASE_URL = `${HOST}/api/`;
export function api_url(path) {
    return `${BASE_URL}${path}`;
}