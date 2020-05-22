<template>
  <div>
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
            label="Discovered Before:"
            label-for="to-date"
            label-cols-sm="3"
            label-align="right"
          >
            <b-form-datepicker id="to-date" v-model="form.to" />
          </b-form-group>
          <b-form-group
            label="Discovered After:"
            label-for="from-date"
            label-cols-sm="3"
            label-align="right"
          >
            <b-form-datepicker id="from-date" v-model="form.from" />
          </b-form-group>
          <b-form-group
            label="Source:"
            label-for="source-select"
            label-cols-sm="3"
            label-align="right"
          >
            <b-form-select id="source-select" v-model="form.source" :options="source_options"></b-form-select>
          </b-form-group>
        </b-collapse>

        <b-button-group id="submit-group" class="float-right">
          <b-button to="/db">Reset</b-button>
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
    <div
      id="leads"
      v-else
      v-infinite-scroll="loadMore"
      infinite-scroll-disabled="disable_loading"
      infinite-scroll-distance="10"
    >
      <div v-bind:key="lead.id" v-for="lead in leads" class="row justify-content-center">
        <Lead v-bind="lead" header-link />
      </div>
    </div>
    <div id="spinner-container" class="row justify-content-center" v-if="loading">
      <b-spinner />
    </div>
  </div>
</template>

<script>
import Lead from "./Lead.vue";
import { mapActions, mapGetters } from "vuex";
import infiniteScroll from "vue-infinite-scroll";

export default {
  name: "FilterLeads",
  directives: {
    infiniteScroll
  },
  props: {
    query: Object
  },
  components: {
    Lead
  },
  data() {
    const query = this.query || {};
    return {
      error: null,
      loading: true,
      leads: [],
      form: {
        filter: query.filter,
        from: query.from,
        to: query.to,
        source: query.source || null
      },
      page: 0,
      page_count: 1
    };
  },
  methods: {
    ...mapActions({
      filterLeads: "leads/filter"
    }),
    loadMore() {
      const filter = this.query;

      this.page += 1;
      this.loading = true;

      this.filterLeads({ params: filter, page: this.page })
        .then(() => {
          this.leads = this.leads.concat(this.getFilter(filter, this.page));
          this.page_count = this.getFilterPages(filter);
          this.loading = false;
        })
        .catch(err => {
          this.loading = false;
          this.error = err;
        });
    },
    clearForm() {
      this.form = {
        filter: undefined,
        from: undefined,
        to: undefined,
        source: null
      };
    },
    submitSearch() {
      this.$router.push(this.search_path);
    },
    clean_filter() {
      return Object.fromEntries(
        Object.entries(this.form).filter(([, value]) => !!value)
      );
    }
  },
  computed: {
    ...mapGetters({
      getFilter: "leads/filter-get",
      getFilterPages: "leads/filter-pages"
    }),
    no_results() {
      return !this.loading && this.leads.length === 0;
    },
    search_path() {
      return {
        path: "/db",
        query: this.clean_filter()
      };
    },
    reached_end() {
      return this.page >= this.page_count;
    },
    disable_loading() {
      return this.loading || this.no_results || this.reached_end;
    },
    source_options() {
      return [
        { value: null, text: "Any Source" },
        {
          label: "Federal",
          options: [
            "Federal Agency - Executive",
            "Federal Agency - Judicial",
            "Federal Agency - Legislative"
          ]
        },
        {
          label: "State / Regional",
          options: [
            "State/Local Govt",
            "Interstate Agency",
            "Native Sovereign Nation"
          ]
        },
        {
          label: "Local",
          options: ["City", "County"]
        }
      ];
    }
  },
  mounted() {
    this.loadMore();
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
</style>