export const STORE_USER = 'STORE_USER';
export const CLEAR_USER = 'CLEAR_USER';

export default {
    namespaced: true,
    state: {
        user: null,
    },
    mutations: {
        [STORE_USER](state, user) {
            state.user = user;
        },
        [CLEAR_USER](state) {
            state.user = null;
        }
    },
    getters: {
        signedIn: (state) => !!state.user,
    }
}