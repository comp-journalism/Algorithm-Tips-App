<template>
  <div id="app">
    <b-navbar type="dark" variant="dark" sticky>
      <b-navbar-nav class="mr-auto">
        <b-nav-item :active="activeOn('/')" href="//algorithmtips.org">Home</b-nav-item>
        <b-nav-item :active="activeOn('/db')" to="/db">Database</b-nav-item>
        <b-nav-item :active="activeOn('/alerts')" to="/alerts">Alerts</b-nav-item>
        <b-nav-item :active="activeOn('/flags')" to="/flags">Flags</b-nav-item>
      </b-navbar-nav>
      <b-navbar-nav>
        <b-nav-item :active="activeOn('/help')" to="/help">Help</b-nav-item>
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
  },
  methods: {
    activeOn(path) {
      return this.$route.path === path;
    }
  }
};
</script>

<style lang="stylus">
#main {
  margin-top: 2em;
  max-width: 55em;
}

#b-toaster-top-right {
  margin-top: 5em;
}
</style>
