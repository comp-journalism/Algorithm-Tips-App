import axios from 'axios';
import { api_url } from '../api';

export const STORE_LEAD = 'STORE_LEAD';

export default {
    namespaced: true,
    // caches leads that we've already looked up
    state: () => { return {}; },
    mutations: {
        [STORE_LEAD](state, lead) {
            state[lead.id] = lead;
        }
    },
    actions: {
        async load({ commit, state }, id) {
            if (state[id]) {
                // we already loaded this. do nothing
                return;
            }

            try {
                const res = await axios.get(api_url(`lead/${id}`));
                commit(STORE_LEAD, res.data);
            } catch (error) {
                console.error(error);
                // TODO: actual error handling
                throw error;
            }
        }
    },
    getters: {
        find: (state) => (id) => state[Number(id)] || null,
    }
};