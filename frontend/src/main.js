import Vue from 'vue';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import store_cfg from './store';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';

import App from './App.vue';
import Lead from './components/Lead.vue';

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
      path: '/lead/:id', component: Lead, props: {
        title: "Algorithm for Fall Risk Assessment & Interventions",
        info: [
          { title: "Jurisdiction", body: "Federal" },
          { title: "Agency", body: "Centers for Disease Control (CDC)" },
          { title: "Main Topics", body: "Health, Safety" },
          { title: "People & Organizations", body: "UNC Medical School" }
        ],
        ratings: [
          {
            title: 'Negative Societal Impact', score: 6.6, comments: [
              { comment: 'Lorum ipsum dolorum', score: 6 },
              { comment: 'Lorum ipsum dolorum', score: 7 },
              { comment: 'Lorum ipsum dolorum', score: 7 },
              { comment: 'Lorum ipsum dolorum', score: 6 }
            ]
          },
          { title: 'Size of Impact', score: 8.0, comments: [] },
          { title: 'Potential for Controversy', score: 4.0, comments: [] },
          { title: 'Surprising', score: 9.0, comments: [] },
        ],
        source: "https://www.cdc.gov/steadi/pdf/provider/steadi-rx/STEADIRx-Algorithm_Final.pdf",
        cache: "#",
        quote: "Assists healthcare providers as to the best way to increase patient mobility without the risk of falling. Assists healthcare providers as to the best way to mobility without the risk"
      }
    }
  ]
});

const store = new Vuex.Store(store_cfg);

new Vue({
  store, router,
  render: fn => fn(App),
}).$mount('#app');
