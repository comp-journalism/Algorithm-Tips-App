<template>
  <div>
    <b-nav-item v-show="loggedIn" @click="signout">Logout</b-nav-item>
    <b-nav-item v-show="!loggedIn" id="signin-button" ref="signin-button">Login with Google</b-nav-item>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";

export default {
  name: "GoogleButton",
  mounted() {
    // eslint-disable-next-line no-undef
    gapi.load("auth2", () => {
      // eslint-disable-next-line no-undef
      this.auth2 = gapi.auth2.init({
        // TODO: but this in a cfg file
        client_id:
          "741161465779-iarif5gv7i2shgk80gmleg1trdtpb4hp.apps.googleusercontent.com"
      });

      this.auth2.currentUser.listen(this.signin.bind(this));

      // the click handler is only used to
      this.auth2.attachClickHandler(this.$refs["signin-button"], {}, () => {});
    });
  },
  data: () => {
    return {
      auth2: null
    };
  },
  computed: {
    ...mapGetters({
      loggedIn: "user/signedIn"
    })
  },
  methods: {
    ...mapActions({
      login: "user/login",
      logout: "user/logout"
    }),
    async signout() {
      try {
        await this.auth2.signOut();
        await this.logout();

        this.$bvToast.toast("You have been logged out.", {
          title: "Logout successful."
        });
      } catch (err) {
        this.loginError(err, false);
      }
    },
    loginError(err, login = true) {
      const type = login ? "Login" : "Logout";
      console.error(err);
      this.$bvToast.toast(`Unable to ${type}: ${err.message}.`, {
        title: `${type} failed.`,
        autoHideDelay: 10000,
        variant: "danger"
      });
    },
    signin(user) {
      if (!user.wc) {
        // logout --- but this is called by gapi so w/e
        return;
      }
      this.login(user)
        .then(() => {
          this.$bvToast.toast("You have been logged in.", {
            title: "Login successful."
          });
        })
        .catch(err => {
          this.loginError(err);
        });
    }
  }
};
</script>