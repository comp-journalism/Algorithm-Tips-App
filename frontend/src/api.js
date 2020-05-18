const BASE_URL = "http://localhost:8080/api/";
export function api_url(path) {
    return `${BASE_URL}${path}`;
}