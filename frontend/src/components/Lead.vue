<template>
  <div class="lead-box">
    <b-card no-body :header-bg-variant="lead.flagged ? 'warning' : 'default'">
      <template v-slot:header>
        <div class="d-flex justify-content-between align-items-center">
          <router-link :to="page_url" v-if="headerLink" class="header-link">
            <h5>{{ lead.name }}</h5>
          </router-link>
          <h5 v-else>{{ lead.name }}</h5>
          <b-button size="sm" @click="setFlag" v-if="!lead.flagged" class="flag-button">
            <b-spinner small class="flag-pending" v-show="flagPending" />Add Flag
          </b-button>
          <b-button size="sm" @click="unsetFlag" v-else class="flag-button">
            <b-spinner small class="flag-pending" v-show="flagPending" />Remove Flag
          </b-button>
        </div>
      </template>
      <b-card-body>
        <p class="quote">{{ lead.description }}</p>
        <!-- prettyhtml-preserve-whitespace -->
        <div class="source">
          <external-link :href="lead.link">{{ lead.link }}</external-link>&nbsp;
          (<external-link class="cache-link" v-if="cache" :href="cache">Cache</external-link>)
        </div>
        <!-- prettyhtml-preserve-whitespace -->
        <div class="found-by">Found via a search for &ldquo;<external-link :href="query_url">{{ lead.query_term }}</external-link>&rdquo; on {{ discovered }}. Published here on {{ published }}.</div>

        <h5>Additional Info</h5>
        <dl class="row">
          <dt class="col-sm-3 text-right">Jurisdiction</dt>
          <dd class="col-sm-9">{{ lead.jurisdiction }}</dd>
          <dt class="col-sm-3 text-right">Agency</dt>
          <dd class="col-sm-9">{{ lead.source }}</dd>
          <dt class="col-sm-3 text-right">Main Topics</dt>
          <dd class="col-sm-9">{{ lead.topic }}</dd>
          <dt class="col-sm-3 text-right">People &amp; Organizations</dt>
          <dd class="col-sm-9">
            <template v-if="people_orgs.length > 0">{{ people_orgs.join(", ") }}</template>
            <template v-else>
              <em class="text-muted">None found</em>
            </template>
          </dd>
        </dl>

        <h5 v-if="ratings_split.length">Crowd Ratings</h5>
      </b-card-body>
      <b-list-group flush>
        <!-- TODO: these bits are slowing down renders. not sure how much effort is worth spending on the perf here -->
        <b-list-group-item v-for="rating in ratings_split" :key="rating.title">
          <div v-b-toggle:[id+rating.title]>
            <b-icon-chevron-right class="when-closed" />
            <b-icon-chevron-down class="when-open" />
            <span class="rating-title">{{ rating.title }}</span>
            <b-progress :max="4" class="w-25 float-right inline-bar" variant="info">
              <b-progress-bar :value="rating.score - 1"></b-progress-bar>
            </b-progress>
            <span class="score-display float-right">{{ rating.score.toFixed(1) }} / 5</span>
          </div>

          <b-collapse :id="id+rating.title">
            <b-table-lite
              v-if="rating.comments.length"
              class="comment-table"
              striped
              :items="rating.comments"
            ></b-table-lite>
            <span v-else>
              <em class="text-muted">No rating information available.</em>
            </span>
          </b-collapse>
        </b-list-group-item>
      </b-list-group>
    </b-card>
    <b-modal
      id="flag-remove-dialog"
      v-if="confirmRemove"
      ref="delete-modal"
      centered
      title="Are you sure?"
      ok-title="Remove Flag"
      ok-variant="danger"
      @hidden="cancelRemove"
      @ok="commitRemove"
      :visible="pendingDeletion"
    >
      <p>Removing this flag will immediately remove it from this page. Are you sure?</p>
    </b-modal>
  </div>
</template>

<script>
import moment from "moment";
import { mapGetters, mapActions } from "vuex";
import externalLink from "./external-link.vue";
import sentence_case from "../sentence-case";

export default {
  name: "Lead",
  components: {
    "external-link": externalLink
  },
  props: { id: Number, headerLink: Boolean, confirmRemove: Boolean },
  data: () => {
    return {
      flagPending: false,
      pendingDeletion: false
    };
  },
  methods: {
    ...mapActions({
      updateFlag: `leads/updateFlag`
    }),
    redirect_login() {
      this.$router.push({
        path: "/login",
        query: {
          redirect: this.$route.fullPath
        }
      });
    },
    async setFlag() {
      if (!this.signedIn) {
        this.redirect_login();
        return;
      }

      try {
        this.flagPending = true;
        await this.updateFlag({ id: this.id, flag: true });
      } catch (err) {
        console.error("Unable to set flag", err);
      } finally {
        this.flagPending = false;
      }
    },
    unsetFlag() {
      if (!this.signedIn) {
        this.redirect_login();
        return;
      }

      if (this.confirmRemove) {
        this.pendingDeletion = true;
      } else {
        this.commitRemove();
      }
    },
    cancelRemove() {
      this.pendingDeletion = false;
    },
    async commitRemove() {
      this.pendingDeletion = false;
      try {
        this.flagPending = true;
        await this.updateFlag({ id: this.id, flag: false });

        this.$emit("remove-flag", this.id);
      } catch (err) {
        console.error("Unable to unset flag", err);
      } finally {
        this.flagPending = false;
      }
    }
  },
  computed: {
    ...mapGetters({
      find: "leads/find",
      signedIn: "user/signedIn"
    }),
    lead() {
      return this.find(this.id);
    },
    page_url() {
      return `/lead/${this.id}`;
    },
    cache() {
      return `https://algorithm-tips.s3.us-east-2.amazonaws.com/documents/${this.id}.${this.lead.document_ext}`;
    },
    query_url() {
      return `https://www.google.com/search?hl=en&q=%22${encodeURIComponent(
        this.lead.query_term
      )}%22+site%3A.gov+-site%3A.nih.gov&as_qdr=w1&lr=en&num=100`;
    },
    people_orgs() {
      const people = JSON.parse(this.lead.people) || {};
      const orgs = JSON.parse(this.lead.organizations) || {};

      const merged = Object.entries(people).concat(Object.entries(orgs));
      merged.sort(([, a], [, b]) => b - a);

      return merged.map(([name]) => name);
    },
    discovered() {
      const dt = moment(this.lead.discovered_dt);

      return dt.format("MMMM Do, YYYY");
    },
    published() {
      const dt = moment(this.lead.published_dt);

      return dt.format("MMMM Do, YYYY");
    },
    ratings_split() {
      const KEYS = ["controversy", "magnitude", "societal_impact", "surprise"];
      const LABELS = [
        "Potential for Controversy",
        "Number of People Impacted",
        "Negative Societal Impact",
        "Surprising, Unusual, or Unexpected"
      ];
      const mapper = obj =>
        KEYS.map((key, ix) => {
          return {
            category: key,
            label: LABELS[ix],
            score: 5 - obj[key] + 1,
            comment: sentence_case(obj[`${key}_explanation`])
          };
        });

      const init = obj => {
        return {
          title: obj.label,
          total_score: 0,
          get score() {
            return this.total_score / this.comments.length;
          },
          comments: []
        };
      };

      return Object.values(
        this.lead.ratings.flatMap(mapper).reduce((result, obj) => {
          if (!result[obj.category]) {
            result[obj.category] = init(obj);
          }

          result[obj.category].total_score += obj.score;
          result[obj.category].comments.push({
            score: obj.score,
            comment: obj.comment
          });
          return result;
        }, {})
      );
    }
  }
};
</script>

<style lang="stylus">
.lead-box {
  margin-bottom: 2em;

  p.quote {
    margin-bottom: 0;
  }

  .card-header h5 {
    margin-bottom: 0;
    display: inline;
  }

  .card-body h5 {
    margin-top: 1rem;
  }

  .card-body {
    padding-bottom: 0;
  }

  dd {
    margin-bottom: 0.1rem;
  }

  .inline-bar {
    display: inline-flex;
    margin-top: 0.25rem;
  }

  .score-display {
    margin-right: 1em;
  }

  .comment-table {
    margin-top: 1em;
  }

  .found-by {
    font-style: italic;
  }

  .collapsed > .when-open, .not-collapsed > .when-closed {
    display: none;
  }

  .rating-title {
    padding-left: 1em;
  }

  a.header-link {
    color: initial;
  }

  .flag-pending {
    margin-right: 1em;
  }

  .flag-button {
    min-width: 7em;
  }
}
</style>