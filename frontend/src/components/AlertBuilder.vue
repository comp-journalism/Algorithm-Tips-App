<template>
  <login-required>
    <div>
      <div class="row">
        <h2>
          <template v-if="edit">Edit</template>
          <template v-else>Create</template> Alert
        </h2>
      </div>
      <div class="row">
        <b-form @submit.prevent="submit" class="w-100">
          <b-form-group label="Keyword Filter:" for="filter">
            <b-form-input
              id="filter"
              v-model="form.filter"
              placeholder="<input keyword filter terms>"
            ></b-form-input>
          </b-form-group>
          <b-form-group label="Source Filter:" for="source">
            <source-selector v-model="form.sources" />
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

          <b-button-group class="float-right">
            <b-button @click="testFilter">Test Filter</b-button>
            <b-button type="submit" variant="primary">Submit</b-button>
          </b-button-group>
        </b-form>
      </div>
      <div class="mt-5 row justify-contents-center" v-if="loading || testResults !== null">
        <b-spinner v-if="loading" />
        <p v-else-if="testResults.length === 0">
          <em>No results found.</em>
        </p>
        <Lead v-else v-for="id in testResults" :id="id" :key="id" />
      </div>
    </div>
  </login-required>
</template>

<script>
import Vue from "vue";
import LoginRequired from "./LoginRequired";
import SourceSelector from "./SourceSelector";
import Lead from "./Lead";
import { frequency_options } from "../constants";
import { mapActions, mapGetters } from "vuex";

export default {
  name: "AlertBuilder",
  components: { LoginRequired, Lead, SourceSelector },
  props: ["id"],
  data() {
    return {
      form: {
        filter: "",
        sources: {},
        frequency: 0,
        recipient: ""
      },
      testResults: null,
      loading: false
    };
  },
  computed: {
    ...mapGetters("user", ["email"]),
    ...mapGetters("alerts", ["find"]),
    ...mapGetters("leads", { getFilter: "filter-get" }),
    freqs() {
      return frequency_options;
    },
    edit() {
      return !!this.id;
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
    ...mapActions("leads", ["filter"]),
    async testFilter() {
      const query = {
        ...this.form.sources
      };
      if (this.form.filter) {
        query.filter = this.form.filter;
      }

      this.loading = true;
      await this.filter({
        page: 1,
        flagged: false,
        params: query
      });

      this.testResults = this.getFilter(query, 1, false);
      this.loading = false;
    },
    async submit() {
      if (this.form.recipient === "") {
        this.form.recipient = this.email;
      }

      if (this.id) {
        // this is an edit
        try {
          const res = await this.update({
            ...this.form,
            id: this.id
          });

          this.$router.push({
            path: "/alerts"
          });

          this.$nextTick(() => {
            if (res.notes) {
              for (const note of res.notes) {
                this.$bvToast.toast(note, {
                  title: "Note",
                  autoHideDelay: 15000
                });
              }
            }
          });
        } catch (err) {
          this.$bvToast.toast(`Unable to update alert: ${err.message}`, {
            title: "Error",
            variant: "danger"
          });
        }
      } else {
        try {
          const res = await this.create(this.form);

          this.$router.push({
            path: "/alerts"
          });

          this.$nextTick(() => {
            if (res.notes) {
              for (const note of res.notes) {
                this.$bvToast.toast(note, {
                  title: "Note",
                  autoHideDelay: 15000
                });
              }
            }
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