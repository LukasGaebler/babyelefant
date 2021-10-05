<template>
  <div v-if="datacollection != null">
    <line-chart
      id="myChart"
      :chart-data="datacollection"
      :options="this.myOptions"
    ></line-chart>
  </div>
</template>

<script>
import LineChart from "../components/LineChart";

export default {
  components: {
    LineChart,
  },
  props: ["apiData", "typeOfData"],
  data() {
    return {
      datacollection: null,
      myOptions: {
        scales: {
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
              },
            },
          ],
        },
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  mounted() {
    this.fillData();
  },
  methods: {
    fillData() {
      if (this.typeOfData === "abstand") {
        if (this.apiData != undefined) {
          this.datacollection = {
            labels: this.apiData[0].map(
              (x) =>
                "" +
                new Date(x).getDate().toString().padStart("0", 2) +
                "." +
                (new Date(x).getMonth() + 1).toString().padStart("0", 2) +
                " " +
                new Date(x).getHours() +
                ":" +
                new Date(x).getMinutes()
            ),
            datasets: [
              {
                label: "minimaler Abstand",
                backgroundColor: "#a3ddcb",
                borderColor: "#8185e2",
                data: this.apiData[2],
                fill: false,
              },
              {
                label: "durchschnittlicher Abstand",
                backgroundColor: "#03506f",
                borderColor: "#03506f",
                data: this.apiData[1],
                fill: false,
              },
            ],
          };
        } else {
          this.datacollection = {};
        }
      }
      if (this.typeOfData === "masken") {
        if (this.apiData != undefined) {
          this.datacollection = {
          labels: this.apiData[0].map(
            (x) =>
              "" +
              new Date(x).getDate().toString().padStart("0", 2) +
              "." +
              (new Date(x).getMonth() + 1).toString().padStart("0", 2) +
              " " +
              new Date(x).getHours() +
              ":" +
              new Date(x).getMinutes()
          ),
          datasets: [
            {
              label: "Masken in %",
              backgroundColor: "#8185e2",
              borderColor: "#8185e2",
              data: this.apiData[1],
              fill: true,
            },
          ],
        };
        } else {
          this.datacollection = {};
        }
      }
    },
    getRandomInt() {
      return Math.floor(Math.random() * (50 - 5 + 1)) + 5;
    },
  },
};
</script>

<style>
.small {
  height: 600px;
}
</style>
