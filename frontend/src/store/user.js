import { api_url } from '../api';
import axios from 'axios';
import EventBus from '../event-bus';

export const STORE_USER = 'STORE_USER';
export const CLEAR_USER = 'CLEAR_USER';
export const SET_LOGIN_STATUS = 'SET_LOGIN_STATUS';

export default {
    namespaced: true,
    state: {
        user: null,
        loggedIn: false,
    },
    mutations: {
        [STORE_USER](state, user) {
            state.user = user;
        },
        [CLEAR_USER](state) {
            state.user = null;
        },
        [SET_LOGIN_STATUS](state, status) {
            state.loggedIn = status;
        }
    },
    actions: {
        async login({ commit }, user) {
            commit(STORE_USER, user);
            await axios({
                method: "POST",
                url: api_url("auth/signin"),
                data: { id_token: user.wc.id_token },
                headers: {
                    "Content-Type": "application/json"
                },
                withCredentials: true
            });

            commit(SET_LOGIN_STATUS, true);
            EventBus.$emit('login');
        },
        async logout({ commit }) {
            await axios({
                method: 'GET',
                url: api_url('auth/signout'),
                withCredentials: true
            });

            commit(SET_LOGIN_STATUS, false);
            EventBus.$emit('logout');
        }
    },
    getters: {
        signedIn: (state) => state.loggedIn,
        email: (state) => state.user ? state.user.Tt.Du : '',
    }
}