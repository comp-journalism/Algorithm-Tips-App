import Vue from 'vue';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import App from './App.vue';
import store_cfg from './store';
import HelloWorld from './components/HelloWorld';

Vue.config.productionTip = false;

Vue.use(VueRouter);
Vue.use(Vuex);

const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '/', component: HelloWorld, props: { msg: 'Router test' } },
    { path: '/:msg', component: HelloWorld, props: true },
  ]
});

const store = new Vuex.Store(store_cfg);

new Vue({
  store, router,
  render: fn => fn(App),
}).$mount('#app');
