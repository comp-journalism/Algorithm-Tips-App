<template>
  <div id="app">
    <b-navbar type="dark" variant="dark" sticky>
      <b-navbar-nav class="mr-auto">
        <b-nav-item to="/">Home</b-nav-item>
        <b-nav-item to="/db">Database</b-nav-item>
        <b-nav-item to="/alerts">Alerts</b-nav-item>
        <b-nav-item to="/flags">Flags</b-nav-item>
      </b-navbar-nav>
      <div id="signin-button" class="g-signin2"></div>
    </b-navbar>
    <div id="main" class="container">
      <router-view :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import { mapMutations } from "vuex";
import { STORE_USER } from "./store/user";
import axios from "axios";
import { api_url } from "./api";

export default {
  name: "App",
  mounted() {
    // eslint-disable-next-line no-undef
    gapi.signin2.render("signin-button", {
      onsuccess: this.login
    });
  },
  methods: {
    login(user) {
      console.log(user);
      this.storeUser(user);
      axios({
        method: "POST",
        url: api_url("auth/signin"),
        data: { id_token: user.wc.id_token },
        headers: {
          "Content-Type": "application/json"
        },
        withCredentials: true
      })
        .then(res => {
          console.log("login succeeded", res);
        })
        .catch(res => {
          console.error(res);
        });
    },
    ...mapMutations({
      storeUser: `user/${STORE_USER}`
    })
  }
};
</script>

<style lang="stylus">
#main {
  margin-top: 2em;
  max-width: 47em;
}
</style>
