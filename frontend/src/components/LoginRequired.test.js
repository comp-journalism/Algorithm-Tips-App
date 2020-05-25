import LoginRequired from './LoginRequired.vue';
import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vue from 'vue';
import Vuex from 'vuex';
import VueRouter from 'vue-router';

const localVue = createLocalVue();
localVue.use(Vuex);
localVue.use(VueRouter);

describe('LoginRequired', () => {
    let store;
    let signedIn;
    let router;

    beforeEach(() => {
        signedIn = false;
        const user = {
            namespaced: true,
            getters: {
                signedIn: jest.fn(() => signedIn)
            }
        };

        store = new Vuex.Store({ modules: { user } });
        router = new VueRouter();
        router.push('/login-required');
    });

    it('should redirect to login if not signed in', async () => {
        shallowMount(LoginRequired, {
            localVue,
            store,
            router,
        });

        await Vue.nextTick();
        expect(router.currentRoute.path).toBe('/login');
        expect(router.currentRoute.query).toEqual({
            redirect: '/login-required'
        });
    });

    it('should not redirect to login if signed in', async () => {
        signedIn = true;
        shallowMount(LoginRequired, {
            localVue,
            store,
            router,
        });

        await Vue.nextTick();

        expect(router.currentRoute.path).toBe('/login-required');
    });

    it('should not render contents when not logged in', () => {
        const el = shallowMount(LoginRequired, {
            localVue, store, router,
            slots: { default: '<div id="test-item">test</div>' }
        });

        expect(el.find('#test-item').exists()).toBe(false);
    });

    it('should render contents when logged in', () => {
        signedIn = true;
        const el = shallowMount(LoginRequired, {
            localVue, store, router,
            slots: { default: '<div id="test-item">test</div>' }
        });

        expect(el.find('#test-item').exists()).toBe(true);
    });

    it('should not render a wrapper element', () => {
        signedIn = true;
        const slot = '<div id="test-item">test</div>';
        const el = shallowMount(LoginRequired, {
            localVue, store, router,
            slots: { default: slot }
        });

        expect(el.html()).toBe(slot);

    });
})