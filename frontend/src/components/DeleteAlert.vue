<template>
  <ApiHandler
    successTitle="Alert Deleted"
    errorTitle="Error Deleting Alert"
    loadingTitle="Deleting Alert..."
    :request="request"
  >
    Your alert has been deleted. You will not longer receive emails about it.
    <template
      v-slot:error
    >There was an error while trying to delete your alert:</template>
  </ApiHandler>
</template>

<script>
import ApiHandler from "./ApiHandler";
import axios from "axios";
import { api_url } from "../api";

export default {
  name: "DeleteAlert",
  props: {
    token: String
  },
  components: {
    ApiHandler
  },
  methods: {
    request() {
      return axios.get(api_url("alert/delete"), {
        params: {
          token: this.token
        }
      });
    }
  }
};
</script>