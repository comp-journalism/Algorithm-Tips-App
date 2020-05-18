<template>
  <div id="app">
    <b-navbar type="dark" variant="dark" sticky>
      <b-navbar-nav>
        <b-nav-item to="/">Home</b-nav-item>
        <b-nav-item to="/db">Database</b-nav-item>
        <b-nav-item to="/alerts">Alerts</b-nav-item>
        <b-nav-item to="/flags">Flags</b-nav-item>
      </b-navbar-nav>
    </b-navbar>
    <div class="container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: "App"
};
</script>

<style lang="stylus"></style>
