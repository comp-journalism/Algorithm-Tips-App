<template>
  <div>
    <slot name="signout">
      <b-nav-item v-show="loggedIn" @click="signout">Logout</b-nav-item>
    </slot>
    <div ref="signin-button">
      <slot>
        <b-nav-item v-show="!loggedIn" id="signin-button">Login with Google</b-nav-item>
      </slot>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import auth2 from "../auth2";

export default {
  name: "GoogleButton",
  props: {
    noListen: Boolean,
  },
  async mounted() {
    this.auth2 = await auth2();

    if (!this.noListen) {
      this.auth2.currentUser.listen(this.signin);
    }

    this.auth2.attachClickHandler(this.$refs["signin-button"], {}, () => {});

    if (this.auth2.isSignedIn.get()) {
      this.signin(this.auth2.currentUser.get());
    }
  },
  data: () => {
    return {
      auth2: null,
    };
  },
  computed: {
    ...mapGetters({
      loggedIn: "user/signedIn",
    }),
  },
  methods: {
    ...mapActions({
      login: "user/login",
      logout: "user/logout",
      updateFlags: "leads/updateAllFlags",
      clearFlags: "leads/clearAllFlags",
      clearAlerts: "alerts/clear",
    }),
    async signout() {
      try {
        await this.auth2.signOut();
        await this.logout();

        this.clearFlags();
        this.clearAlerts();
        this.$bvToast.toast("You have been logged out.", {
          title: "Logout successful.",
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
        variant: "danger",
      });
    },
    async signin(user) {
      if (!user.getAuthResponse().id_token) {
        // no token present---this is a logout call triggered by the currentUser listener
        return;
      }
      try {
        await this.login(user);

        this.$bvToast.toast("You have been logged in.", {
          title: "Login successful.",
        });
      } catch (err) {
        this.loginError(err);
      }

      try {
        await this.updateFlags();
      } catch (err) {
        console.error(err);

        this.$bvToast.toast("Unable to update flags.", {
          title: "Error",
          variant: "danger",
        });
      }
    },
  },
};
</script>