<template>
  <login-required>
    <div>
      <div class="row">
        <h2>Create Alert</h2>
      </div>
      <div class="row">
        <b-form @submit.prevent="submit" class="w-100">
          <b-form-group label="Relevant Key Terms:" for="filter">
            <b-form-input id="filter" v-model="form.filter" placeholder="<input key terms>"></b-form-input>
          </b-form-group>
          <b-form-group label="Source Filter:" for="source">
            <b-form-select id="source" v-model="form.source" :options="sources"></b-form-select>
          </b-form-group>
          <b-form-group label="How Often:" for="frequency">
            <b-form-select id="frequency" v-model="form.frequency" :options="freqs"></b-form-select>
          </b-form-group>
          <b-form-group label="Email:" for="recipient">
            <b-form-input
              :required="!email"
              id="recipient"
              v-model="form.recipient"
              type="email"
              :placeholder="email"
            ></b-form-input>
          </b-form-group>

          <b-button class="float-right" type="submit">Submit</b-button>
        </b-form>
      </div>
    </div>
  </login-required>
</template>

<script>
import Vue from "vue";
import LoginRequired from "./LoginRequired";
import { source_options, frequency_options } from "../constants";
import { mapActions, mapGetters } from "vuex";

export default {
  name: "AlertBuilder",
  components: { LoginRequired },
  props: ["id"],
  data() {
    return {
      form: {
        filter: "",
        source: null,
        frequency: 0,
        recipient: ""
      }
    };
  },
  computed: {
    ...mapGetters("user", ["email"]),
    ...mapGetters("alerts", ["find"]),
    sources() {
      return source_options;
    },
    freqs() {
      return frequency_options;
    }
  },
  async mounted() {
    if (!this.id) {
      return;
    }

    try {
      await this.load(this.id);
      Vue.set(this, "form", this.find(this.id));
    } catch (err) {
      this.$bvToast.toast(`Unable to load alert for editing: ${err.message}`, {
        title: "Error",
        variant: "danger"
      });
    }
  },
  methods: {
    ...mapActions("alerts", ["update", "create", "load"]),
    async submit() {
      if (this.form.recipient === "") {
        this.form.recipient = this.email;
      }

      if (this.id) {
        // this is an edit
        try {
          await this.update({
            ...this.form,
            id: this.id
          });

          this.$router.push({
            path: "/alerts"
          });
        } catch (err) {
          this.$bvToast.toast(`Unable to update alert: ${err.message}`, {
            title: "Error",
            variant: "danger"
          });
        }
      } else {
        try {
          await this.create(this.form);

          this.$router.push({
            path: "/alerts"
          });
        } catch (err) {
          this.$bvToast.toast(`Unable to create alert: ${err.message}`, {
            title: "Error",
            variant: "danger"
          });
        }
      }
    }
  }
};
</script>