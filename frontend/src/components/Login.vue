<template>
  <div>
    <div class="row justify-content-center">
      <p>In order to access this functionality, you must be logged in.</p>
    </div>
    <div class="row justify-content-center">
      <GoogleButton no-listen>
        <b-button>Login with Google</b-button>
      </GoogleButton>
    </div>
  </div>
</template>

<script>
import GoogleButton from "./GoogleButton";
import EventBus from "../event-bus";
import { mapGetters } from "vuex";

const DEFAULT_REDIRECT = "/db";

export default {
  name: "Login",
  components: { GoogleButton },
  props: {
    redirect: String
  },
  computed: {
    ...mapGetters({ signedIn: "user/signedIn" })
  },
  methods: {
    go_redirect() {
      this.$router.push(this.redirect || DEFAULT_REDIRECT);
    }
  },
  mounted() {
    if (this.signedIn) {
      this.go_redirect();
    }
    EventBus.$on("login", this.go_redirect);
  },
  beforeDestroy() {
    EventBus.$off("login", this.go_redirect);
  }
};
</script>