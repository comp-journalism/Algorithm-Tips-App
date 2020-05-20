<template>
  <div class="lead-box">
    <b-card no-body>
      <template v-slot:header>
        <router-link :to="page_url" v-if="headerLink" class="header-link">
          <h5>{{ name }}</h5>
        </router-link>
        <h5 v-else>{{ name }}</h5>
        <a class="float-right" href="#">Add Flag</a>
      </template>
      <b-card-body>
        <p class="quote">{{ description }}</p>
        <div class="source">
          <a :href="link">Source</a>&nbsp;
          <a class="cache-link" v-if="cache" :href="cache">(Cache)</a>
        </div>
        <div
          class="found-by"
        >Found via a search for &ldquo;{{ query_term }}&rdquo; on {{ discovered }}</div>

        <h5>Additional Info</h5>
        <dl class="row">
          <dt class="col-sm-4">Jurisdiction</dt>
          <dd class="col-sm-8">{{ jurisdiction }}</dd>
          <dt class="col-sm-4">Agency</dt>
          <dd class="col-sm-8">{{ source }}</dd>
          <dt class="col-sm-4">Main Topics</dt>
          <dd class="col-sm-8">{{ topic }}</dd>
          <dt class="col-sm-4">People &amp; Organizations</dt>
          <dd class="col-sm-8">{{ people_orgs.join(", ") }}</dd>
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
            <b-progress :max="5" class="w-25 float-right inline-bar" variant="info">
              <b-progress-bar :value="rating.score"></b-progress-bar>
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
              <em>No rating information available.</em>
            </span>
          </b-collapse>
        </b-list-group-item>
      </b-list-group>
    </b-card>
  </div>
</template>

<script>
import moment from "moment";
export default {
  name: "Lead",
  props: {
    id: Number,
    name: String,
    description: String,
    link: String,
    cache: String,
    ratings: Array,
    jurisdiction: String,
    source: String,
    topic: String,
    people: String,
    organizations: String,
    query_term: String,
    discovered_dt: String,
    "header-link": Boolean
  },
  computed: {
    page_url() {
      return `/lead/${this.id}`;
    },
    people_orgs() {
      const people = JSON.parse(this.people);
      const orgs = JSON.parse(this.organizations);

      const filtration = ([, count]) => count >= 10;
      const merged = Object.entries(people)
        .concat(Object.entries(orgs))
        .filter(filtration);
      merged.sort(([, a], [, b]) => b - a);

      // const merged = people_fil.concat(orgs_fil);
      // merged.sort(([, a], [, b]) => a - b);
      return merged.map(([name]) => name);
    },
    discovered() {
      const dt = moment(this.discovered_dt);

      return dt.format("MMMM Do, YYYY");
    },
    ratings_split() {
      const KEYS = ["controversy", "magnitude", "societal_impact", "surprise"];
      const LABELS = [
        "Potential for Controversy",
        "Size of Impact",
        "Negative Societal Impact",
        "Surprising"
      ];
      const mapper = obj =>
        KEYS.map((key, ix) => {
          return {
            category: key,
            label: LABELS[ix],
            score: 5 - obj[key] + 1,
            comment: obj[`${key}_explanation`]
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
        this.ratings.flatMap(mapper).reduce((result, obj) => {
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
}
</style>