let HANDLE = null;

// TODO: put this in a cfg file
const KEY = "741161465779-iarif5gv7i2shgk80gmleg1trdtpb4hp.apps.googleusercontent.com";

// Provides singleton access to the GAPI auth2 handle.
export default async function auth2() {
    if (HANDLE) { return HANDLE; }
    if (!window.gapi) {
        throw Error('Google API is inaccessible');
    }

    const promise = new Promise((resolve) => {
        // eslint-disable-next-line no-undef
        gapi.load("auth2", () => {
            // eslint-disable-next-line no-undef
            HANDLE = gapi.auth2.init({
                client_id: KEY
            });

            resolve(HANDLE);
        });
    });

    return await promise;
}