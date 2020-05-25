import { mount, shallowMount, createLocalVue } from '@vue/test-utils';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';
import Vue from 'vue';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import Lead from './Lead.vue';
import data from '../../test/test-lead.json';

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(IconsPlugin);
localVue.use(Vuex);
localVue.use(VueRouter);

describe('Lead', () => {
    let store;
    let router;
    let leads_module;
    let users_module;

    beforeEach(() => {
        router = new VueRouter();
        leads_module = {
            namespaced: true,
            getters: {
                find: jest.fn(() => () => data),
            }
        };

        users_module = {
            namespaced: true,
            getters: {
                signedIn: jest.fn(() => false),
            },
        };

        store = new Vuex.Store({
            modules: { leads: leads_module, user: users_module }
        });
    });

    it('matches the snapshot', () => {
        const wrapper = shallowMount(Lead, { localVue, store, propsData: { id: data.id } });
        expect(wrapper).toMatchSnapshot();
    });

    it('should redirect to login when adding a flag while logged out', async () => {
        router.push('/lead/1420');
        const wrapper = mount(Lead, { localVue, store, router, propsData: { id: data.id } });
        await wrapper.find('.flag-button').trigger('click');

        await Vue.nextTick();

        expect(router.currentRoute.path).toBe("/login");
        expect(router.currentRoute.query).toEqual({
            redirect: "/lead/1420"
        });
    });
});