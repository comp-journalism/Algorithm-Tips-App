import Vue from 'vue';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import store_cfg from './store';

import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';

import App from './App.vue';
import SingleLead from './components/SingleLead.vue';
import FilterLeads from './components/FilterLeads.vue';
import Login from './components/Login.vue';
import PathNotFound from './components/PathNotFound.vue';
import Alerts from './components/Alerts.vue';
import AlertBuilder from './components/AlertBuilder.vue';
import HowThisWorks from './components/HowThisWorks.vue';
import ConfirmEmail from './components/ConfirmEmail.vue';
import DeleteAlert from './components/DeleteAlert.vue';
import Unsubscribe from './components/Unsubscribe.vue';
//import VueAnalytics from 'vue-analytics';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';

Vue.config.productionTip = false;

// Configuration VueAnalytics -- to integrate Google analytics with the app
//Vue.use(VueAnalytics, {
//  id: 'UA-180997791-1',
//  router
//});

Vue.use(VueRouter);
Vue.use(Vuex);
Vue.use(BootstrapVue);
Vue.use(IconsPlugin);

const BASE_TITLE = "Algorithm Tips - Resources and leads for investigating algorithms in society";

const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '/', redirect: { path: '/db' } },
    {
      path: '/lead/:id', component: SingleLead, props: true,
      meta: { title: `Lead | ${BASE_TITLE}` }
    },
    {
      path: '/db', component: FilterLeads, props: (route) => { return { query: route.query, flagged: false }; },
      meta: { title: `Database | ${BASE_TITLE}` }
    },
    {
      path: '/flags', component: FilterLeads, props: (route) => { return { query: route.query, flagged: true }; },
      meta: { title: `Flagged Leads | ${BASE_TITLE}` }
    },
    {
      path: '/login', component: Login, props: (route) => { return { redirect: route.query.redirect }; },
      meta: { title: `Login | ${BASE_TITLE}` }
    },
    {
      path: '/alerts', component: Alerts,
      meta: { title: `Alerts | ${BASE_TITLE}` }
    },
    {
      path: '/alerts/create', component: AlertBuilder,
      meta: { title: `Create Alert | ${BASE_TITLE}` }
    },
    {
      path: '/alerts/edit', component: AlertBuilder, props: (route) => { return { id: route.query.id }; },
      meta: { title: `Edit Alert | ${BASE_TITLE}` }
    },
    {
      path: '/help', component: HowThisWorks,
      meta: { title: `Help | ${BASE_TITLE}` }
    },
    {
      path: '/confirm-email', component: ConfirmEmail,
      meta: { title: `Confirm Email | ${BASE_TITLE}` },
      props: ({ query }) => ({ token: query.token }),
    },
    {
      path: '/delete-alert', component: DeleteAlert,
      meta: { title: `Delete Alert | ${BASE_TITLE}` },
      props: ({ query }) => ({ token: query.token }),
    },
    {
      path: '/unsubscribe', component: Unsubscribe,
      meta: { title: `Unsubscribe | ${BASE_TITLE}` },
      props: ({ query }) => ({ token: query.token }),
    },
    {
      path: '*', component: PathNotFound,
      meta: { title: `Error 404: File Not Found | ${BASE_TITLE}` }
    }
  ]
});

router.beforeEach((to, _from, next) => {
  if (to.meta && to.meta.title) {
    document.title = to.meta.title;
  }

  next();
});

const store = new Vuex.Store(store_cfg);

new Vue({
  store, router,
  render: fn => fn(App),
}).$mount('#app');
