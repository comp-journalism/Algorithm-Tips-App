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
  data: () => {
    return { lead: null };
  },
  computed: {
    ...mapGetters({ getLead: "leads/find" })
  },
  mounted() {
    this.loadLead(this.id).then(() => {
      console.log(this.getLead);
      this.lead = this.getLead(this.id);
    });
  },
  components: {
    Lead: Lead
  }
};
</script>