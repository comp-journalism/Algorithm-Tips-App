import axios from 'axios';
import { api_url } from '../api';

export const STORE_LEAD = 'STORE_LEAD';
export const STORE_FILTER = 'STORE_FILTER';

function filterKey(params) {
    const entries = Object.entries(params);
    entries.sort(([a], [b]) => (a < b) ? -1 : 1);

    return entries.map(([key, val]) => `${key}=${val}`).join('&');
}

export default {
    namespaced: true,
    // caches leads that we've already looked up
    state: () => {
        return {
            leads: {},
            filters: {},
        };
    },
    mutations: {
        [STORE_LEAD](state, lead) {
            state.leads[lead.id] = lead;
        },
        [STORE_FILTER](state, { ids, filter }) {
            state.filters[filterKey(filter)] = ids;
        }
    },
    actions: {
        async load({ commit, state }, id) {
            if (state.leads[id]) {
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
        },
        async filter({ commit, state }, params) {
            console.log(params);
            if (state.filters[filterKey(params)]) {
                return;
            }

            try {
                const res = await axios.get(api_url('leads'), {
                    params,
                });

                res.data.forEach(lead => commit(STORE_LEAD, lead));
                commit(STORE_FILTER, { filter: params, ids: res.data.map(({ id }) => id) });
            } catch (error) {
                console.error(error);
                throw error;
            }
        }
    },
    getters: {
        find: (state) => (id) => state.leads[Number(id)] || null,
        'filter-get': (state) => (filter) => (state.filters[filterKey(filter)] || []).map(id => state.leads[id]),
    }
};