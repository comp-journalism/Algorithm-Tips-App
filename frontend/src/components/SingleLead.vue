<template>
  <div class="row justify-content-center">
    <Lead v-if="loaded" :id="id" />
    <em v-else-if="error">Unable to load lead: {{ error.message }}</em>
    <b-spinner v-else />
  </div>
</template>

<script>
import Lead from "./Lead.vue";
import { mapActions, mapGetters } from "vuex";

export default {
  name: "SingleLead",
  props: {
    id: String
  },
  methods: {
    ...mapActions({
      loadLead: "leads/load"
    })
  },
  data: () => {
    return {
      error: null,
      loaded: false
    };
  },
  computed: {
    ...mapGetters({ getLead: "leads/find" })
  },
  mounted() {
    this.loadLead(this.id)
      .then(() => {
        this.loaded = true;
      })
      .catch(err => {
        this.error = err;
      });
  },
  components: {
    Lead: Lead
  }
};
</script>