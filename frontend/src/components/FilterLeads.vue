<template>
  <login-required :disabled="!flagged">
    <div id="leads-container">
      <div class="row">
        <b-form @submit.prevent="submitSearch" class="col-sm-12" id="lead-filter">
          <b-form-input id="filter-input" v-model="form.filter" placeholder="Search..." />
          <div id="advanced-toggle" v-b-toggle:advanced-filters>
            <b-icon-chevron-right class="when-closed" />
            <b-icon-chevron-down class="when-open" />
            <span>Advanced Filters</span>
          </div>
          <b-collapse id="advanced-filters">
            <b-form-group
              label="Published On or After:"
              label-for="from-date"
              label-cols-sm="3"
              label-align="right"
            >
              <b-form-datepicker id="from-date" v-model="form.from" />
            </b-form-group>
            <b-form-group
              label="Published On or Before:"
              label-for="to-date"
              label-cols-sm="3"
              label-align="right"
            >
              <b-form-datepicker id="to-date" v-model="form.to" />
            </b-form-group>
            <b-form-group label="Included Sources:" label-cols-sm="3" label-align="right">
              <source-selector v-model="sources" />
            </b-form-group>
          </b-collapse>

          <b-button-group id="submit-group" class="float-right">
            <b-button :to="$route.path">Reset</b-button>
            <b-button id="submit-search" type="submit" :to="search_path" variant="primary">Search</b-button>
          </b-button-group>
        </b-form>
      </div>
      <div class="row justify-content-center" v-if="error">
        <p>
          <em>Unable to load results: {{ error.message }}.</em>
        </p>
      </div>
      <div class="row justify-content-center" v-else-if="no_results">
        <p>
          <em>No results found</em>
        </p>
      </div>
      <div v-else>
        <div v-if="num_results > 0" class="row">
          <p>
            <em>{{ num_results }} Results Found</em>
          </p>
        </div>
        <div
          id="leads"
          v-infinite-scroll="loadMore"
          infinite-scroll-disabled="disable_loading"
          infinite-scroll-distance="10"
          class="row justify-content-center"
        >
          <Lead
            :key="id"
            v-for="id in lead_ids"
            :id="id"
            header-link
            :confirm-remove="flagged"
            @remove-flag="leadFlagRemoved"
          />
        </div>
      </div>
      <div id="spinner-container" class="row justify-content-center" v-if="loading">
        <b-spinner />
      </div>
    </div>
  </login-required>
</template>

<script>
import Vue from "vue";
import Lead from "./Lead.vue";
import { mapActions, mapGetters } from "vuex";
import infiniteScroll from "vue-infinite-scroll";
import EventBus from "../event-bus";
import LoginRequired from "./LoginRequired";
import SourceSelector from "./SourceSelector";
import isEqual from "lodash.isequal";

export default {
  name: "FilterLeads",
  directives: {
    infiniteScroll
  },
  props: {
    flagged: Boolean
  },
  components: {
    "login-required": LoginRequired,
    Lead,
    SourceSelector
  },
  data() {
    return {
      error: null,
      loading: true,
      lead_ids: [],
      form: this.initForm(this.$route.query),
      sources: this.initSource(this.$route.query),
      page: 0,
      page_count: 1,
      num_results: 0
    };
  },
  methods: {
    ...mapActions({
      filterLeads: "leads/filter"
    }),
    initForm(query) {
      return {
        filter: query.filter,
        from: query.from,
        to: query.to
      };
    },
    initSource(query) {
      return {
        federal: query.federal,
        regional: query.regional,
        local: query.regional
      };
    },
    loadMore() {
      const filter = this.query;

      this.page += 1;
      this.loading = true;

      this.filterLeads({
        params: filter,
        page: this.page,
        flagged: this.flagged
      })
        .then(() => {
          this.lead_ids = this.lead_ids.concat(
            this.getFilter(filter, this.page, this.flagged)
          );
          const meta = this.getFilterPages(filter, this.flagged);
          this.page_count = meta.page_count;
          this.num_results = meta.num_results;
          this.loading = false;
        })
        .catch(err => {
          this.loading = false;
          this.error = err;
        });
    },
    updateForm() {
      Vue.set(this, "form", this.initForm(this.query));
      Vue.set(this, "sources", this.initSource(this.query));
    },
    leadFlagRemoved(id) {
      if (this.flagged) {
        this.lead_ids = this.lead_ids.filter(lid => lid !== id);
      }
    },
    submitSearch() {
      if (isEqual(this.clean_filter(), this.query)) {
        return;
      }
      this.$router.push(
        this.search_path,
        () => {},
        err => {
          console.error(err);
        }
      );
    },
    clean_filter() {
      const filter = {
        ...this.form,
        ...this.sources
      };

      return Object.fromEntries(
        Object.entries(filter).filter(([, value]) => !!value)
      );
    },
    redirect_login() {
      this.$router.push({
        path: "/login",
        query: { redirect: this.$route.fullPath }
      });
    },
    newSearch() {
      Vue.set(this, "lead_ids", []);
      this.page = 0;
      this.page_count = 1;
      this.loadMore();
    }
  },
  computed: {
    ...mapGetters({
      getFilter: "leads/filter-get",
      getFilterPages: "leads/filter-pages",
      getLead: "leads/find",
      signedIn: "user/signedIn"
    }),
    query() {
      return this.$route.query;
    },
    no_results() {
      return !this.loading && this.lead_ids.length === 0;
    },
    search_path() {
      return {
        path: this.$route.path,
        query: this.clean_filter()
      };
    },
    reached_end() {
      return this.page >= this.page_count;
    },
    disable_loading() {
      return this.loading || this.no_results || this.reached_end;
    }
  },
  async mounted() {
    if (this.flagged && !this.signedIn) {
      EventBus.$on("login", this.newSearch);
    } else {
      this.newSearch();
    }
  },
  beforeDestroy() {
    EventBus.$off("login", this.newSearch);
  },
  watch: {
    query() {
      this.updateForm();
      this.newSearch();
    }
  }
};
</script>

<style lang="stylus" scoped>
#lead-filter {
  margin-bottom: 2em;
}

#submit-group {
  margin-top: 1em;
}

.collapsed > .when-open, .not-collapsed > .when-closed {
  display: none;
}

#advanced-toggle {
  margin-top: 0.5em;
}

#advanced-toggle > span {
  margin-left: 0.5em;
}

#spinner-container {
  margin-bottom: 2em;
}

#leads-container {
  margin-bottom: 3em;
}
</style>