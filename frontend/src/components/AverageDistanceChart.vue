<template>
  <div class="">
    <div class="card">
      <canvas id="chart"></canvas>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js';

export default {
  mounted() {
    this.fillData();
  },
  methods: {
    fillData() {
      /* eslint-disable no-unused-vars */
      var ctx = document.getElementById('chart');
      var chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["12:00", "12:05", "12:10", "12:15", "12:20", "12:25"],
          datasets: [
            {
              label: "Durchschnittlich gemessener Abstand",
              backgroundColor: "#f87979",
              data: [1.25,3,2.75,4.8,1.30,2.5]
            }
          ]
        }
        
      });
      /* eslint-enable no-unused-vars */
    },
    getRandomInt() {
      return Math.floor(Math.random() * (50 - 5 + 1)) + 5;
    }
  }
};
</script>

<style scoped>

</style>
