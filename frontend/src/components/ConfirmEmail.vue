<template>
  <div>
    <div class="row">
      <h2>{{ title }}</h2>
    </div>
    <div class="row">
      <b-spinner v-if="confirming" />
      <p v-else-if="success">Your email has been confirmed!</p>
      <p v-else>There was an error confirming your email: {{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { api_url } from "../api";

export default {
  name: "ConfirmEmail",
  props: {
    token: String
  },
  data: () => ({
    success: false,
    error: null
  }),
  computed: {
    confirming() {
      return !this.success && !this.error;
    },
    title() {
      if (this.confirming) {
        return "Confirming Your Email...";
      } else if (this.success) {
        return "Email Confirmed";
      } else {
        return "Error Confirming Email";
      }
    }
  },
  async mounted() {
    try {
      await axios.get(api_url("auth/confirm"), {
        params: {
          token: this.token
        }
      });
      this.success = true;
    } catch (err) {
      if (err.response) {
        console.log(err.response.data);
        this.error = err.response.data.reason;
      }
    }
  }
};
</script>