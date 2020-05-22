<template>
  <div id="app">
    <b-navbar type="dark" variant="dark" sticky>
      <b-navbar-nav class="mr-auto">
        <b-nav-item to="/">Home</b-nav-item>
        <b-nav-item to="/db">Database</b-nav-item>
        <b-nav-item to="/alerts">Alerts</b-nav-item>
        <b-nav-item to="/flags">Flags</b-nav-item>
      </b-navbar-nav>
      <b-navbar-nav>
        <GoogleButton />
      </b-navbar-nav>
    </b-navbar>
    <div id="main" class="container position-relative">
      <router-view :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import GoogleButton from "./components/GoogleButton";

export default {
  name: "App",
  components: {
    GoogleButton
  }
};
</script>

<style lang="stylus">
#main {
  margin-top: 2em;
  max-width: 47em;
}
</style>
