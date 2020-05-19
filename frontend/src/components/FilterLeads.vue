<template>
  <div>
    <div class="row">
      <b-form @submit.prevent="submitSearch" class="col-sm-12" id="lead-filter">
        <b-form-input v-model="form.filter" placeholder="Search..." />
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
        </b-collapse>

        <b-button-group id="submit-group" class="float-right">
          <b-button to="/db">Reset</b-button>
          <b-button type="submit" :to="search_path" variant="primary">Search</b-button>
        </b-button-group>
      </b-form>
    </div>
    <div class="row justify-content-center" v-if="loading">
      <b-spinner />
    </div>
    <div class="row justify-content-center" v-else-if="no_results">
      <p>
        <em>No results found</em>
      </p>
    </div>
    <div id="#leads" v-else>
      <div v-bind:key="lead.id" v-for="lead in leads" class="row justify-content-center">
        <Lead v-bind="lead" header-link />
      </div>
      <b-pagination-nav
        :number-of-pages="page_count"
        v-model="page"
        no-page-detect
        use-router
        :link-gen="linkGen"
      />
    </div>
  </div>
</template>

<script>
import Lead from "./Lead.vue";
import { mapActions, mapGetters } from "vuex";

export default {
  name: "FilterLeads",
  props: {
    query: Object
  },
  components: {
    Lead
  },
  data() {
    return {
      leads: null,
      form: {
        filter: this.query.filter,
        from: this.query.from,
        to: this.query.to,
        source: this.query.source
      },
      page_count: 1
    };
  },
  methods: {
    ...mapActions({
      filterLeads: "leads/filter"
    }),
    linkGen(pagenum) {
      return {
        path: "/db",
        query: { ...this.clean_filter(), page: pagenum }
      };
    },
    updateData() {
      this.leads = null;
      const filter = this.query;
      this.filterLeads({ params: filter, page: this.page }).then(() => {
        this.leads = this.getFilter(filter, this.page);
        this.page_count = this.getFilterPages(filter);
      });
    },
    clearForm() {
      this.filter = {
        filter: undefined,
        from: undefined,
        to: undefined,
        source: undefined
      };
    },
    submitSearch() {
      this.$router.push(this.search_path);
    },
    clean_filter() {
      return Object.fromEntries(
        Object.entries(this.form).filter(([, value]) => value !== undefined)
      );
    }
  },
  computed: {
    ...mapGetters({
      getFilter: "leads/filter-get",
      getFilterPages: "leads/filter-pages"
    }),
    page() {
      return this.query.page || 1;
    },
    loading() {
      return this.leads === null;
    },
    no_results() {
      return this.leads !== null && this.leads.length === 0;
    },
    search_path() {
      return {
        path: "/db",
        query: {
          ...this.clean_filter(),
          page: 1
        }
      };
    }
  },
  mounted() {
    this.updateData();
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
</style>