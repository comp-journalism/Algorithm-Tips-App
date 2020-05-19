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
        [STORE_FILTER](state, { num_pages, page, ids, filter }) {
            const key = filterKey(filter);
            if (!state.filters[key]) {
                state.filters[key] = {
                    num_pages,
                    page_contents: {}
                };
            }

            state.filters[key].page_contents[page] = ids;
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
        async filter({ commit, state }, { params, page }) {
            console.log(params, page);
            const key = filterKey(params);
            if (state.filters[key] && state.filters[key].page_contents[page]) {
                return;
            }

            try {
                const res = await axios.get(api_url('leads'), {
                    params: { ...params, page: page },
                });

                res.data.leads.forEach(lead => commit(STORE_LEAD, lead));

                const ids = res.data.leads.map(({ id }) => id);
                commit(STORE_FILTER, {
                    filter: params,
                    num_pages: res.data.num_pages,
                    ids, page
                });
            } catch (error) {
                console.error(error);
                throw error;
            }
        }
    },
    getters: {
        find: (state) => (id) => state.leads[Number(id)] || null,
        'filter-get': (state) => (filter, page) => {
            const meta = state.filters[filterKey(filter)];
            if (!meta) {
                return [];
            }

            return meta.page_contents[page].map(id => state.leads[id]);
        },
        'filter-pages': (state) => (filter) => {
            const meta = state.filters[filterKey(filter)];
            if (!meta) {
                return null;
            }

            return meta.num_pages;
        }
    }
};