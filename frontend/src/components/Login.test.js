import { shallowMount, createLocalVue } from '@vue/test-utils';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';
import Vue from 'vue';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import Login from './Login';
import EventBus from '../event-bus';

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(IconsPlugin);
localVue.use(Vuex);
localVue.use(VueRouter);

describe('Lead', () => {
    let store;
    let router;
    let users_module;
    let shouldRedirect;

    beforeEach(() => {
        router = new VueRouter();
        router.push('/login');

        shouldRedirect = false;
        users_module = {
            namespaced: true,
            getters: {
                signedIn: jest.fn(() => shouldRedirect),
            },
        };

        store = new Vuex.Store({
            modules: { user: users_module }
        });
    });

    it('should not redirect on load if not signed in', () => {
        shallowMount(Login, {
            store, router, localVue, propsData: {
                redirect: '/test'
            }
        });

        expect(router.currentRoute.fullPath).toBe('/login');
    });

    it('should redirect on load if signed in', () => {
        shouldRedirect = true;

        shallowMount(Login, {
            store, router, localVue, propsData: {
                redirect: '/test'
            }
        });

        expect(router.currentRoute.fullPath).toBe('/test');
    });

    it('should redirect when the "login" event is sent onto the EventBus', async () => {
        // since this is a global event bus, other tests may be running. remove their event handlers
        EventBus.$off('login');
        shallowMount(Login, {
            store, router, localVue, propsData: {
                redirect: '/test'
            }
        });

        expect(router.currentRoute.fullPath).toBe('/login');

        EventBus.$emit('login');
        await Vue.nextTick();
        expect(router.currentRoute.fullPath).toBe('/test');
    });
});