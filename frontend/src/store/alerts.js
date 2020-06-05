// const DUMMY_DATA = {
//     1: {
//         id: 1,
//         source: "test",
//         frequency: "test",
//         filter: "test",
//         recipient: "test@test.test"
//     },
//     2: {
//         id: 2,
//         source: "test",
//         frequency: "test",
//         filter: "test",
//         recipient: "test@test.test"
//     }
// };

export const REMOVE_ALERT = 'REMOVE_ALERT';
export const ADD_ALERT = 'ADD_ALERT';
import Vue from 'vue';
import axios from 'axios';
import { api_url } from '../api';

export default {
    namespaced: true,
    state: {
        alerts: {}
    },
    mutations: {
        [REMOVE_ALERT](state, id) {
            Vue.delete(state.alerts, id);
        },
        [ADD_ALERT](state, alert) {
            Vue.set(state.alerts, alert.id, alert);
        },
    },
    getters: {
        all: (state) => {
            return Object.values(state.alerts);
        },
        find: (state) => (id) => {
            return state.alerts[Number(id)];
        },
    },
    actions: {
        async create({ commit }, alert) {
            const res = await axios.post(api_url('alert/create'), alert, {
                withCredentials: true
            });
            alert.id = res.data.id;

            commit(ADD_ALERT, alert);
            return res.data;
        },
        async update({ commit }, alert) {
            const res = await axios.put(api_url(`alert/${alert.id}`), alert, {
                withCredentials: true
            });

            commit(ADD_ALERT, alert);
            return res.data;
        },
        async remove({ commit }, id) {
            await axios.delete(api_url(`alert/${id}`), {
                withCredentials: true
            });

            commit(REMOVE_ALERT, id);
        },
        async list({ commit }) {
            const res = await axios.get(api_url('alert/list'), {
                withCredentials: true
            });

            res.data.alerts.forEach(alert => commit(ADD_ALERT, alert));
        },
        async load({ commit, state }, id) {
            if (state.alerts[Number(id)]) {
                // already loaded. done
                return;
            }

            const res = await axios.get(api_url(`alert/${id}`), {
                withCredentials: true
            });

            commit(ADD_ALERT, res.data);
        },
        clear({ commit, state }) {
            for (const key of Object.keys(state.alerts)) {
                commit(REMOVE_ALERT, key);
            }
        }
    }
}