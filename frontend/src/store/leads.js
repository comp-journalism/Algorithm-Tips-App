import axios from 'axios';
import { api_url } from '../api';
import Vue from 'vue';

export const STORE_LEAD = 'STORE_LEAD';
export const STORE_FILTER = 'STORE_FILTER';
export const SET_FLAG = 'SET_FLAG';
export const SET_LAST_QUERY = 'SET_LAST_QUERY';

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
            last_query: {
                [true]: {},
                [false]: {}
            }
        };
    },
    mutations: {
        [STORE_LEAD](state, lead) {
            Vue.set(state.leads, lead.id, lead);
        },
        [STORE_FILTER](state, { num_pages, num_results, page, ids, filter }) {
            const key = filterKey(filter);
            if (!state.filters[key]) {
                Vue.set(state.filters, key, {
                    num_pages,
                    num_results,
                    page_contents: {}
                });
            }

            Vue.set(state.filters[key].page_contents, page, ids);
        },
        [SET_FLAG](state, { id, flag }) {
            Vue.set(state.leads[id], 'flagged', flag);
        },
        [SET_LAST_QUERY](state, { flagged, query }) {
            Vue.set(state.last_query, flagged, query);
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
        async filter({ commit, state }, { params, page, flagged }) {
            const key = filterKey(params);
            if (state.filters[key] && state.filters[key].page_contents[page]) {
                return;
            }

            const endpoint = flagged ? 'leads/flagged' : 'leads';

            try {
                const res = await axios.get(api_url(endpoint), {
                    params: { ...params, page: page },
                    withCredentials: true
                });

                res.data.leads.forEach(lead => commit(STORE_LEAD, lead));

                const ids = res.data.leads.map(({ id }) => id);
                commit(STORE_FILTER, {
                    filter: { ...params, flagged },
                    num_pages: res.data.num_pages,
                    num_results: res.data.num_results,
                    ids, page
                });
            } catch (error) {
                console.error(error);
                throw error;
            }
        },
        async updateFlag({ commit }, { id, flag }) {
            console.log(id, flag);
            if (flag) {
                await axios.put(
                    api_url(`flag/${id}`),
                    {},
                    { withCredentials: true }
                );
            } else {
                await axios.delete(api_url(`flag/${id}`), {
                    withCredentials: true
                });
            }

            commit(SET_FLAG, { id, flag: flag });
        },
        async updateAllFlags({ commit, state }) {
            const ids = Object.keys(state.leads).map(Number);

            const res = await axios.post(api_url('flag/list'), ids, { withCredentials: true });
            res.data.flags.forEach((flag, ix) => commit(SET_FLAG, { id: ids[ix], flag }));
        },
        clearAllFlags({ commit, state }) {
            // used on logout to set everything back to "Add Flag"
            Object.keys(state.leads).forEach(id => commit(SET_FLAG, { id: Number(id), flag: false }));
        },
        setLastQuery({ commit }, opts) {
            commit(SET_LAST_QUERY, opts);
        }
    },
    getters: {
        find: (state) => (id) => state.leads[Number(id)] || null,
        'filter-get': (state) => (filter, page, flagged) => {
            const meta = state.filters[filterKey({ ...filter, flagged })];
            if (!meta) {
                return [];
            }

            return meta.page_contents[page];
        },
        'filter-pages': (state) => (filter, flagged) => {
            const meta = state.filters[filterKey({ ...filter, flagged })];
            if (!meta) {
                return null;
            }

            return { page_count: meta.num_pages, num_results: meta.num_results };
        },
        lastQuery: (state) => (flagged) => {
            return state.last_query[flagged];
        }
    }
};