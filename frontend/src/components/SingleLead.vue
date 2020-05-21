<template>
  <div class="row justify-content-center">
    <Lead v-if="lead" v-bind="lead" />
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
  computed: {
    ...mapGetters({ getLead: "leads/find" }),
    lead() {
      return this.getLead(this.id);
    }
  },
  mounted() {
    this.loadLead(this.id);
  },
  components: {
    Lead: Lead
  }
};
</script>