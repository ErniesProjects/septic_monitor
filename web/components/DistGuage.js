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
            refresh_interval: 2000,
      }),
      mounted() {
            this.chart = new Chart(document.getElementById('dist-gauge'), {
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
            });  // this.chart

            setInterval(() => {
                this.distance = 10 + Math.floor(Math.random() * 5)
                this.chart.options.animation.duration = 0;
                this.chart.data.datasets[0].data.pop();
                this.chart.data.datasets[0].data.pop();
                this.chart.data.datasets[0].data.push(this.distance);
                this.chart.data.datasets[0].data.push(this.max_distance - this.distance);
                this.chart.update()
            }, this.refresh_interval)
      } // mounted
};


