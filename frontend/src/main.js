import Vue from 'vue';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import store_cfg from './store';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';

import App from './App.vue';
import SingleLead from './components/SingleLead.vue';
import FilterLeads from './components/FilterLeads.vue';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';

Vue.config.productionTip = false;

Vue.use(VueRouter);
Vue.use(Vuex);
Vue.use(BootstrapVue);
Vue.use(IconsPlugin);

const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/lead/:id', component: SingleLead, props: true,
    },
    {
      path: '/db', component: FilterLeads, props: (route) => { return { query: route.query }; },
    }
  ]
});

const store = new Vuex.Store(store_cfg);

new Vue({
  store, router,
  render: fn => fn(App),
}).$mount('#app');
