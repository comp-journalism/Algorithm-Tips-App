<template>
  <login-required>
    <div class="row justify-contents-center">
      <h2>Alerts</h2>
      <b-table-simple striped>
        <colgroup>
          <col class="col-sm-5" />
          <col class="col-sm-1" />
          <col class="col-sm-1" />
          <col class="col-sm-2" />
        </colgroup>
        <b-thead>
          <b-tr>
            <b-th>Source</b-th>
            <b-th>Frequency</b-th>
            <b-th>Keywords</b-th>
            <b-th>Recipient</b-th>
            <b-th></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr :key="alert.id" v-for="alert in alerts">
            <b-td>{{ formatSource(alert.sources) }}</b-td>
            <b-td>{{ formatFrequency(alert.frequency) }}</b-td>
            <b-td>{{ alert.filter }}</b-td>
            <b-td>{{ alert.recipient }}</b-td>
            <b-td class="row-controls text-right">
              <a href @click.prevent="reconfirm(alert.id)">
                <b-icon-exclamation-circle
                  v-if="!alert.confirmed"
                  v-b-popover.hover.top="'This email has not been confirmed and will not receive alerts. If you have not received a confirmation email, click this button to resend it.'"
                  variant="danger"
                  title="Email Not Confirmed"
                />
              </a>
              <router-link :to="edit_path(alert)">
                <b-icon-pencil />
              </router-link>
              <a href @click.prevent="remove(alert)">
                <b-icon-trash />
              </a>
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
      <b-button to="/alerts/create">Create Alert</b-button>
      <b-modal
        ref="delete-modal"
        centered
        title="Are you sure?"
        ok-title="Delete"
        ok-variant="danger"
        @hidden="cancelRemove"
        @ok="commitRemove"
        :visible="pendingDeletion !== null"
      >
        <p>Deleting an alert is permanent. Are you sure you want to do this?</p>
      </b-modal>
    </div>
  </login-required>
</template>

<script>
import LoginRequired from "./LoginRequired";
import { mapGetters, mapActions } from "vuex";
import { frequency_options } from "../constants";
import sentence_case from "../sentence-case";
import axios from "axios";
import { api_url } from "../api";

export default {
  name: "Alerts",
  components: { LoginRequired },
  data() {
    return {
      pendingDeletion: null
    };
  },
  methods: {
    ...mapActions("alerts", {
      listAlerts: "list",
      deleteAlert: "remove"
    }),
    async reconfirm(alert_id) {
      try {
        await axios.get(api_url(`alert/${alert_id}/resend-confirmation`), {
          withCredentials: true
        });

        this.$bvToast.toast("Confirmation Email Sent", {
          title: "Success"
        });
      } catch (err) {
        if (err.response) {
          this.$bvToast.toast(
            `Unable to send confirmation email: ${err.response.data.reason}`,
            {
              title: "Error",
              variant: "danger"
            }
          );
        }
      }
    },
    remove(alert) {
      this.pendingDeletion = alert.id;
    },
    commitRemove() {
      try {
        this.deleteAlert(this.pendingDeletion);
        this.pendingDeletion = null;
      } catch (err) {
        this.$bvToast.toast(`Unable to delete alert: ${err.message}`, {
          title: "Error",
          variant: "danger"
        });
      }
    },
    cancelRemove() {
      this.pendingDeletion = null;
    },
    edit_path(alert) {
      return {
        path: "/alerts/edit",
        query: {
          id: alert.id
        }
      };
    },
    formatSource(source) {
      const result = ["federal", "regional", "local"]
        .map(key => {
          const value = source[key];
          if (value === "exclude") {
            return `No ${sentence_case(key)}`;
          } else if (value === null) {
            return `Any ${sentence_case(key)}`;
          } else {
            return value;
          }
        })
        .join(", ");

      if (result === "") {
        return "Any Source";
      } else {
        return result;
      }
    },
    formatFrequency(freq) {
      const item = frequency_options.find(({ value }) => freq === value);
      if (item) {
        return item.text;
      } else {
        return "Unknown";
      }
    }
  },
  computed: {
    ...mapGetters("alerts", {
      alerts: "all"
    })
  },
  mounted() {
    this.listAlerts();
  }
};
</script>

<style scoped lang="stylus">
.row-controls svg:first-child {
  margin-right: 1em;
}
</style>