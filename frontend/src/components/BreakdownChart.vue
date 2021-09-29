<template>
  <div id="donutChart">
    <div class="card card-custom">
        <h5>Zusammenfassung</h5>
        <hr />
        <div class="card-body">
            <canvas id="donutchart" width="50" height="50"></canvas>
        </div>
        <hr />
        <div id="legend"></div>
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
      var ctx = document.getElementById('donutchart');
      var chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ["Leute die den Abstand halten", "Leute die den Abstand nicht halten"],
          datasets: [
            {
              label: "Data One",
              backgroundColor: "#f87979",
              data: [75,50]
            }
          ]
        },
         options: {
            legend: {
                display: false,
                position: 'bottom'
            },
            legendCallback: (chart) => {
              var text = [];
                        text.push(
                            ` <h6 class="breakdownHeader">${chart.data.labels[0]}: ${chart.data.datasets[0].data[0]}</h5>
                              <h6 class="breakdownHeader">${chart.data.labels[1]}: ${chart.data.datasets[0].data[1]}</h5>
                            `
                        );
                        return text.join("");
            }
        }
        
      });
      /* eslint-enable no-unused-vars */
            document.getElementById('legend').innerHTML = chart.generateLegend();
    },
    getRandomInt() {
      return Math.floor(Math.random() * (50 - 5 + 1)) + 5;
    }
  }
}
</script>

<style>
#donutChart, .card-custom {
    height: 100%;
}
.card-custom h5 {
    padding-left: 15px;
    padding-top: 15px;
}

.breakdownNumber {
  padding-left: 15px;
}

.breakdownHeader {
  padding-left: 10px;
  font-size: 0.85rem;
}
</style>