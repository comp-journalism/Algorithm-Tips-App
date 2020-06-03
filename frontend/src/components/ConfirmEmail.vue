<template>
  <ApiHandler
    successTitle="Email Confirmed"
    errorTitle="Error Confirming Email"
    loadingTitle="Confirming Your Email..."
    :request="request"
  >
    Your email has been confirmed!
    <template v-slot:error>There was an error confirming your email:</template>
  </ApiHandler>
</template>

<script>
import ApiHandler from "./ApiHandler";
import axios from "axios";
import { api_url } from "../api";

export default {
  name: "ConfirmEmail",
  props: {
    token: String
  },
  components: {
    ApiHandler
  },
  methods: {
    request() {
      return axios.get(api_url("auth/confirm"), {
        params: {
          token: this.token
        }
      });
    }
  }
};
</script>