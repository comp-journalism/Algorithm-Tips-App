<template>
  <ApiHandler
    successTitle="You Have Been Unsubscribed"
    errorTitle="Error During Unsubscription..."
    loadingTitle="Unsubscribing..."
    :request="request"
  >
    You have been unsubscribed from all alerts.
    <template
      v-slot:error
    >There was an error while trying to process your unsubscription request:</template>
  </ApiHandler>
</template>

<script>
import ApiHandler from "./ApiHandler";
import axios from "axios";
import { api_url } from "../api";

export default {
  name: "Unsubscribe",
  props: {
    token: String
  },
  components: {
    ApiHandler
  },
  methods: {
    request() {
      return axios.get(api_url("alert/unsubscribe"), {
        params: {
          token: this.token
        }
      });
    }
  }
};
</script>