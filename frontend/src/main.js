import Vue from 'vue';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import App from './App.vue';
import store from './store';

Vue.config.productionTip = false;

Vue.use(VueRouter);
Vue.use(Vuex);

const router = new VueRouter({
  routes: []
});

new Vue({
  render: h => h(App),
  store, router
}).$mount('#app');
