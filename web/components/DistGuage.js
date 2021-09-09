export default {
  name: 'DistGuage',
  template: `
    <div>
        <div class="text-center">Dist: {{ distance }} cm</div>
        <canvas id="dist-gauge"></canvas>
    </div>
  `,
  data: () => ({
        max_distance: 20,
        distance: 15,
        chart: null,
      }),
  mounted() {
        var dg = document.getElementById('dist-gauge');
        this.chart = new Chart(dg, {
          type: 'doughnut',
          data: {
            datasets: [{
              data: [this.distance, this.max_distance - this.distance],
              backgroundColor: [
                'rgb(255, 99, 132)',
                'rgb(54, 162, 235)',
              ],
            }],
          },
          options: {
            tooltips: {
              enabled: false
            },
            hover: {
              mode: null
            }
          }
        });
        setTimeout(() => {
            this.distance = 10;
            this.chart.data.datasets[0].data.pop();
            this.chart.data.datasets[0].data.pop();
            this.chart.data.datasets[0].data.push(this.distance);
            this.chart.data.datasets[0].data.push(this.max_distance - this.distance);
            this.chart.update()
        }, 5000)
  } // mounted
};


