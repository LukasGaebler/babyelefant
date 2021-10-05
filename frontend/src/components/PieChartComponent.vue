<template>
  <div v-if="datacollection != null">
    <pieChart
      id="myChart"
      :chart-data="datacollection"
      :options="this.myOptions"
    ></pieChart>
  </div>
</template>

<script>
import pieChart from "../components/PieChart";

export default {
  components: {
    pieChart,
  },
  props: ["apiData"],
  data() {
    return {
      myOptions: {
        hoverBorderWidth: 20,
        responsive: true,
        maintainAspectration: false,
        animation: {
          duration: 0
        }
      },
      datacollection: null,
    };
  },
  mounted() {
    this.fillData();
  },
  methods: {
    fillData() {
      if (this.apiData != undefined) {
        this.datacollection = {
          hoverBorderWidth: 10,
          labels: ["Keine Maske", "Maske"],
          datasets: [
            {
              label: "Data One",
              backgroundColor: ["#E46651", "#00D8FF"],
              data: this.apiData,
            },
          ],
        };
      }
    },
  },
};
</script>

<style>
</style>