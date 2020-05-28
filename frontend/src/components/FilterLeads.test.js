import { mount, shallowMount, createLocalVue } from '@vue/test-utils';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';
import Vue from 'vue';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import FilterLeads from './FilterLeads.vue';
import data from '../../test/test-lead.json';

const localVue = createLocalVue();
localVue.use(Vuex);
localVue.use(VueRouter);
localVue.use(BootstrapVue);
localVue.use(IconsPlugin);

describe('FilterLeads', () => {
    let store;
    let leads_module;
    let users_module;
    let router;

    beforeEach(() => {
        router = new VueRouter();

        users_module = {
            namespaced: true,
            getters: {
                signedIn: jest.fn(() => false),
            }
        };

        leads_module = {
            namespaced: true,
            actions: {
                load: jest.fn(() => Promise.resolve()),
                filter: jest.fn(() => Promise.resolve()),
            },
            getters: {
                find: jest.fn(() => () => data),
                'filter-get': jest.fn(() => () => [1420]),
                'filter-pages': jest.fn(() => () => 1),
            }
        };

        store = new Vuex.Store({
            modules: { user: users_module, leads: leads_module }
        });
    });

    const makeFilter = (fn) => (query, flagged = false) => fn(FilterLeads, {
        propsData: {
            flagged,
            query,
        },
        localVue,
        store,
        router,
    });

    const shallowFilter = makeFilter(shallowMount);
    const mountFilter = makeFilter((q, flagged, opts) => mount(q, flagged, {
        attachToDocument: true,
        ...opts
    }));

    it('should call filter on mount with the query param values', async () => {
        router.push('/db');
        const query = {
            filter: 'test',
            from: '2020-1-20',
        };

        const el = shallowFilter(query);

        expect(leads_module.actions.filter.mock.calls[0][1]).toEqual({
            flagged: false,
            params: query,
            page: 1,
        });

        await Vue.nextTick();
        expect(el.find('lead-stub').props('id')).toBe(data.id);

        expect(el).toMatchSnapshot();
    });

    it('should set the query string after submitting the search form', async () => {
        const query = {};
        const el = mountFilter(query, false);

        el.find("#filter-input").setValue('test');
        await el.find("#lead-filter").trigger('submit');

        await Vue.nextTick();

        expect(router.currentRoute.query).toEqual({
            filter: 'test'
        });

        el.destroy();
    });

    it('should not search for an empty string', async () => {
        const query = {
            to: '2020-01-01',
        };
        const el = mountFilter(query, false);

        el.find("#filter-input").setValue('');
        await el.find("#lead-filter").trigger('submit');

        await Vue.nextTick();

        expect(router.currentRoute.query).toEqual({
            to: '2020-01-01'
        });

        el.destroy();

    });

    it('should redirect to login if flagged and not logged in', async () => {
        router.push('/flags');
        const el = mountFilter({}, true);

        await Vue.nextTick();
        expect(router.currentRoute.path).toBe('/login');
        expect(router.currentRoute.query).toEqual({
            redirect: '/flags'
        });

        el.destroy();
    });
});