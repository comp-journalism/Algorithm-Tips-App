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
    request: {
      type: Function,
      default: async () => {
        throw Error("no request function provided");
      }
    }
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
  mounted() {
    this.$nextTick(async () => {
      try {
        console.log(this, this.request);
        await this.request();
        this.status = "success";
      } catch (err) {
        this.status = "error";
        if (err.response) {
          console.error(err.response.data);
          this.error = err.response.data.reason;
        } else {
          console.error(err);
        }
      }
    });
  }
};
</script>