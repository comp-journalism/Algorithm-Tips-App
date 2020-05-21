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
    let router;

    beforeEach(() => {
        router = new VueRouter();

        leads_module = {
            namespaced: true,
            actions: {
                load: jest.fn(() => Promise.resolve()),
                filter: jest.fn(() => Promise.resolve()),
            },
            getters: {
                find: jest.fn(),
                'filter-get': jest.fn(() => () => [data]),
                'filter-pages': jest.fn(() => () => 1),
            }
        };

        store = new Vuex.Store({
            modules: { leads: leads_module }
        });
    });

    const makeFilter = (fn) => (query) => fn(FilterLeads, {
        propsData: {
            query,
        },
        localVue,
        store,
        router,
    });

    const shallowFilter = makeFilter(shallowMount);
    const mountFilter = makeFilter((q, opts) => mount(q, {
        attachToDocument: true,
        ...opts
    }));

    it('should call filter on mount with the query param values', async () => {
        const query = {
            filter: 'test',
            from: '2020-1-20',
        };

        const el = shallowFilter(query);

        expect(leads_module.actions.filter.mock.calls[0][1]).toEqual({
            params: query,
            page: 1,
        });

        await Vue.nextTick();
        expect(el.find('lead-stub').props('name')).toBe(data.name);

        expect(el).toMatchSnapshot();
    });

    it('should set the query string after submitting the search form', async () => {
        const query = {};
        const el = mountFilter(query);

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
        const el = mountFilter(query);

        el.find("#filter-input").setValue('');
        await el.find("#lead-filter").trigger('submit');

        await Vue.nextTick();

        expect(router.currentRoute.query).toEqual({
            to: '2020-01-01'
        });

        el.destroy();

    });
});