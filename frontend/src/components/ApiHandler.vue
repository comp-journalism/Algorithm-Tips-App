<template>
  <div>
    <div class="row">
      <h2>{{ title }}</h2>
    </div>
    <div class="row">
      <b-spinner v-if="confirming" />
      <p v-else-if="success">
        <slot></slot>
      </p>
      <p v-else>
        <slot name="error"></slot>
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "ApiHandler",
  props: {
    loadingTitle: String,
    successTitle: String,
    errorTitle: String,
    request: Function
  },
  data() {
    return {
      status: "loading",
      error: null
    };
  },
  computed: {
    confirming() {
      return this.status === "loading";
    },
    success() {
      return this.status === "success";
    },
    title() {
      if (this.confirming) {
        return this.loadingTitle;
      } else if (this.success) {
        return this.successTitle;
      } else {
        return this.errorTitle;
      }
    }
  },
  async mounted() {
    try {
      await this.request();
      this.status = "success";
    } catch (err) {
      this.status = "error";
      if (err.response) {
        console.log(err.response.data);
        this.error = err.response.data.reason;
      }
    }
  }
};
</script>