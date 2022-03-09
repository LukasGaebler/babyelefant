<template>
  <div id="root">
    <div class="content" v-if="data != null">
      <div class="row">
        <div class="col-sm-12">
          <chart :apiData="this.data" :key="this.rerender" />
        </div>
      </div>
      <div class="row" style="margin-top: 1%">
        <div class="col">
          <div class="card custom-card" style="text-align: center">
            <h4>durchschnittlicher Abstand</h4>
            <h5>{{ currentAvg }}</h5>
          </div>
        </div>
        <div class="col">
          <div class="card custom-card" style="text-align: center">
            <h4>minimal Abstand</h4>
            <h5>{{ currentMin }}</h5>
          </div>
        </div>
        <div class="col">
          <div class="card custom-card" style="text-align: center">
            <h4>erkannte Personen</h4>
            <h5>{{ numberOfPeople }}</h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";
import chart from "../components/Chart";

export default {
  props: ["eventId"],
  components: {
    chart,
  },
  data: function() {
    return {
      data: [
        [], //Labels X-Achse
        [], // Average
        [], // Minimum
      ],
      rerender: 0,
      currentMin: 0,
      currentMax: 0,
      currentAvg: 0,
      numberOfPeople: 0,
    };
  },
  mounted() {
    this.getEventData();
  },
  methods: {
    getEventData() {
      api
        .get(process.env.VUE_APP_API_URL + "/distanceData/" + this.eventId)
        .then((data) => {
          var stats = data.data.data;
          var index = stats.length - 10;
          for (index; index < stats.length; index++) {
            this.data[0].push(stats[index]["d_datetime"]);
            this.data[1].push(stats[index]["d_avg"]);
            this.currentAvg = Math.round(stats[index]["d_avg"] * 100) / 100;
            this.data[2].push(stats[index]["d_min"]);
            this.currentMin = Math.round(stats[index]["d_min"] * 100) / 100;
            this.numberOfPeople = stats[index]["d_numberofpeople"];
          }
          this.forceRerender();
        });
    },
    forceRerender() {
      this.rerender += 1;
    },
  },
};
</script>

<style scoped>
.background-white {
  display: flex;
  flex-direction: column;
  justify-content: center;
  background-color: #05386b;
  border-radius: 10px;
  text-align: center;
  color: #edf5e1;
}

.thicc {
  font-weight: 600;
}

.max {
  grid-row: 1;
  grid-column: 1;
}

.avg {
  grid-row: 2;
  grid-column: 1;
}

.min {
  grid-row: 3;
  grid-column: 1;
}

.graph {
  grid-row: 1 / 4;
  background-color: white;
  border-radius: 10px;
}

.count {
  background-color: #afeeee;
  color: #05386b;
}
</style>
