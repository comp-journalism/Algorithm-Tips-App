<script>
import { mapGetters } from "vuex";
import EventBus from "../event-bus";
import auth2 from "../auth2";

export default {
  name: "LoginRequired",
  props: {
    disabled: Boolean
  },
  render() {
    if (this.signedIn || this.disabled) {
      return this.$slots.default;
    } else {
      return null;
    }
  },
  computed: {
    ...mapGetters({
      signedIn: "user/signedIn"
    })
  },
  methods: {
    redirect_login() {
      this.$router.push({
        path: "/login",
        query: {
          redirect: this.$route.fullPath
        }
      });
    }
  },
  async mounted() {
    if (this.disabled) {
      return;
    }

    EventBus.$on("logout", this.redirect_login);

    if (!this.signedIn) {
      try {
        const auth = await auth2();
        if (!auth.isSignedIn.get()) {
          this.redirect_login();
        }
      } catch {
        // unable to authenticate, go to login
        this.redirect_login();
      }
    }
  },
  beforeDestroy() {
    EventBus.$off("logout", this.redirect_login);
  }
};
</script>