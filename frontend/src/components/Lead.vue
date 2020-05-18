<template>
  <div class="lead-box">
    <b-card no-body>
      <template v-slot:header>
        <h5>{{ title }}</h5>
        <a class="float-right" href="#">Add Flag</a>
      </template>
      <b-card-body>
        <p class="quote">&ldquo;&hellip; {{ quote }} &hellip;&rdquo;</p>
        <div class="source">
          <a :href="source">Source</a>&nbsp;
          <a class="cache-link" :href="cache">(Cache)</a>
        </div>

        <h6>Additional Info</h6>
        <dl class="row">
          <template v-for="entry in info">
            <dt :key="entry.title" class="col-sm-4">{{ entry.title }}</dt>
            <dd :key="entry.title" class="col-sm-8">{{ entry.body }}</dd>
          </template>
        </dl>

        <h6>Crowd Ratings</h6>
      </b-card-body>
      <b-list-group flush>
        <b-list-group-item v-for="rating in ratings" :key="rating.title">
          <div v-b-toggle:[rating.title]>
            <span>{{ rating.title }}</span>
            <b-progress :max="10" class="w-25 float-right inline-bar" variant="info">
              <b-progress-bar :value="rating.score"></b-progress-bar>
            </b-progress>
            <span class="score-display float-right">{{ rating.score.toFixed(1) }} / 10</span>
          </div>

          <b-collapse :id="rating.title">
            <b-table
              v-if="rating.comments.length"
              class="comment-table"
              striped
              :items="rating.comments"
            ></b-table>
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
// example props structure
//
// {
//   title: "Algorithm for Fall Risk Assessment & Interventions",
//   info: [
//     { title: "Jurisdiction", body: "Federal" },
//     { title: "Agency", body: "Centers for Disease Control (CDC)" },
//     { title: "Main Topics", body: "Health, Safety" },
//     { title: "People & Organizations", body: "UNC Medical School" }
//   ],
//   ratings: [
//     {
//       title: "Negative Societal Impact",
//       score: 6.6,
//       comments: [
//         { comment: "Lorum ipsum dolorum", score: 6 },
//         { comment: "Lorum ipsum dolorum", score: 7 },
//         { comment: "Lorum ipsum dolorum", score: 7 },
//         { comment: "Lorum ipsum dolorum", score: 6 }
//       ]
//     },
//     { title: "Size of Impact", score: 8.0, comments: [] },
//     { title: "Potential for Controversy", score: 4.0, comments: [] },
//     { title: "Surprising", score: 9.0, comments: [] }
//   ],
//   source:
//     "https://www.cdc.gov/steadi/pdf/provider/steadi-rx/STEADIRx-Algorithm_Final.pdf",
//   cache: "#",
//   quote:
//     "Assists healthcare providers as to the best way to increase patient mobility without the risk of falling. Assists healthcare providers as to the best way to mobility without the risk"
// }
export default {
  name: "Lead",
  props: {
    title: String,
    quote: String,
    source: String,
    cache: String,
    info: Array,
    ratings: Array
  }
};
</script>

<style lang="stylus">
.lead-box {
  max-width: 45em;

  p.quote {
    margin-bottom: 0;
  }

  .card-header h5 {
    margin-bottom: 0;
    display: inline;
  }

  h6 {
    margin-top: 1rem;
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
}
</style>