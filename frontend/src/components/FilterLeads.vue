<template>
  <div>
    <div class="row">
      <b-form class="col-sm-12" id="lead-filter">
        <b-form-input v-model="filter.filter" placeholder="Search..." />
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
            <b-form-datepicker id="to-date" v-model="filter.to" />
          </b-form-group>
          <b-form-group
            label="Discovered After:"
            label-for="from-date"
            label-cols-sm="3"
            label-align="right"
          >
            <b-form-datepicker id="from-date" v-model="filter.from" />
          </b-form-group>
        </b-collapse>

        <b-button-group id="submit-group" class="float-right">
          <b-button @click="clearForm">Reset</b-button>
          <b-button @click="updateData" variant="primary">Search</b-button>
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
    </div>
  </div>
</template>

<script>
import Lead from "./Lead.vue";
import { mapActions, mapGetters } from "vuex";

export default {
  name: "FilterLeads",
  components: {
    Lead
  },
  data() {
    return {
      leads: null,
      filter: {
        filter: this.filter,
        from: this.from,
        to: this.to,
        source: this.source
      }
    };
  },
  methods: {
    ...mapActions({
      filterLeads: "leads/filter"
    }),
    updateData() {
      this.leads = null;
      const filter = Object.fromEntries(
        Object.entries(this.filter).filter(([, value]) => value !== undefined)
      );
      this.filterLeads(filter).then(() => {
        this.leads = this.getFilter(filter);
      });
    },
    clearForm() {
      this.filter = {
        filter: undefined,
        from: undefined,
        to: undefined,
        source: undefined
      };
      this.updateData();
    }
  },
  computed: {
    ...mapGetters({
      getFilter: "leads/filter-get"
    }),
    loading() {
      return this.leads === null;
    },
    no_results() {
      return this.leads !== null && this.leads.length === 0;
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