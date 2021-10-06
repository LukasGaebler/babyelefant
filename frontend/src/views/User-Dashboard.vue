<template>
  <div id="root">
    <h2>DASHBOARD</h2>
    <div class="content" v-if="data != null">
      <div class="row">
        <div class="col-sm-12">
          <div class="card custom-card">
            <chart :apiData="this.data" :key="this.rerender" typeOfData="abstand"/>
          </div>
        </div>
      </div>
      <div class="row" style="margin-top: 1%">
        <div class="col">
          <div class="card custom-card" style="text-align: center">
            <!-- <h4>durchschnittlicher Abstand</h4>
            <h5>{{ currentAvg }}</h5> -->
            <div class="card-body">
              <h5 class="card-title">durchschnittlicher Abstand</h5>
              <p class="card-text">{{currentAvg}}</p>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card custom-card" style="text-align: center">
            <!-- <h4>minimal Abstand</h4>
            <h5>{{ currentMin }}</h5> -->
            <div class="card-body">
              <h5 class="card-title">minimal abstand</h5>
              <p class="card-text">{{currentMin}}</p>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card custom-card" style="text-align: center">
            <!-- <h4>erkannte Personen</h4>
            <h5>{{ numberOfPeople }}</h5> -->
            <div class="card-body">
              <h5 class="card-title">erkannte personen</h5>
              <p class="card-text">{{numberOfPeople}}</p>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card custom-card" style="text-align: center">
            <!-- <h4>Anzahl an Events</h4>
            <h5>{{ numberEvents }}</h5> -->
            <div class="card-body">
              <h5 class="card-title">Anzahl an Events</h5>
              <p class="card-text">{{numberEvents}}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="row" style="margin-top: 1%">
        <div class="col-sm-3">
          <div class="card custom-card" style="text-align: center">
            <div class="card-body">
              <h5 class="card-title">Mask Ratio</h5>
              <pieChart :key="this.rerender" :apiData="this.getMaskRatio()"></pieChart>
            </div>
          </div>
        </div>
        <div class="col-sm-9">
          <div class="card custom-card" style="text-align: center">
            <div class="card-body">
              <h5 class="card-title">Personen mit Masken in %</h5>
              <chart :apiData="this.maskData" :key="this.rerender" typeOfData="masken"/>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";
import chart from "../components/Chart";
import pieChart from "../components/PieChartComponent";

export default {
  data: function() {
    return {
      
      data: [
        [], //Labels X-Achse
        [], // Average
        [], // Minimum
      ],
      maskData: [
        [], //Labels X-Achse
        [], //Mask data in %
      ],
      rerender: 0,
      currentMin: 0,
      currentAvg: 0,
      numberOfPeople: 0,
      numberEvents: 0,
      maskedPeople: 0,
    };
  },
  components: {
    chart,
    pieChart
  },
  mounted() {
    this.getData();
  },
  methods: {
    getData() {
      //Keep function to implement live update later
      setTimeout(()=>{
        this.data = [[],[],[]];
        this.maskData = [[],[]];
        api.get(process.env.VUE_APP_API_URL + "/distanceData/").then((data) => {
          var stats = data.data.data;
          var index = stats.length - 100;
          for (index; index < stats.length; index++) {
            if (stats[index] != undefined) {
              this.data[0].push(new Date(stats[index]["d_datetime"]));
              this.maskData[0].push(new Date(stats[index]["d_datetime"]));
              this.data[1].push(stats[index]["d_avg"]);
              this.currentAvg = Number(stats[index]["d_avg"]);
              this.data[2].push(stats[index]["d_min"]);
              this.currentMin = Number(stats[index]["d_min"]);
              this.numberOfPeople = stats[index]["d_numberofpeople"];
              this.maskedPeople = stats[index]["d_maskedpeople"];
              this.maskData[1].push(this.maskedPeople/this.numberOfPeople*100);
            }
          }
          if (this.data != undefined) {
            this.forceRerender();
          }
        });
      },0);

      api.get(process.env.VUE_APP_API_URL + "/events/").then((data) => {
        var events = data.data.data;
        this.numberEvents = events.length;
      });
    },

    forceRerender() {
      var scrollX = window.scrollX;
      var scrollY = window.scrollY;
      this.rerender += 1;
      this.rerenderPie += 1;
      window.scrollTo(scrollX,scrollY);
    },

    getMaskRatio() {
      return [(this.numberOfPeople - this.maskedPeople), this.maskedPeople];
    }
  },
};
</script>

<style scoped>
/* d .custom-card {
  padding: 10px;
} */


.thicc {
  font-weight: 600;
}

.max {
  grid-row: 1;
  grid-column: 1;
  background-color: #ff6961;
}

.avg {
  grid-row: 2;
  grid-column: 1;
  background-color: #aec6cf;
}

.min {
  grid-row: 3;
  grid-column: 1;
  background-color: #77dd77;
}

.graph {
  grid-row: 1 / 4;
  grid-column: 2/5;
  background-color: white;
  border-radius: 10px;
}

.background-blue {
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 10px;
  text-align: center;
  background-color: #afeeee;
  color: #05386b;
  padding: 0.5rem;
}

.count {
  grid-row: 4;
  background-color: #afeeee;
  color: #05386b;
}

h3 {
  font-size: 28px;
}

h5 {
  text-transform: uppercase;
}

p {
  font-size: 28px;
}

.eventCount {
  grid-row: 4;
  grid-column: 2/3;
}

.maskGraph {
  grid-row: 4/7;
  grid-column: 3/5;
}

@media only screen and (max-width: 600px) {
  .content {
    width: 100%;
    height: auto;
    display: flex;
    flex-direction: column;
  }
}

.card {
  height: 100%;
}
</style>
