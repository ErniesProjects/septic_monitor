export default {
      name: 'DistGuage',
      template: `
        <div>
            <div class="text-center">Dist: {{ distance }} cm</div>
            <canvas id="dist-gauge"></canvas>
        </div>
      `,
      data: () => ({
            maxDistance: 40,  // FIXME
            minDistance: 30,  // FIXME
            distance: null,
            chart: null,
            refresh_interval: 2000,
            colorBg: "rgb(54, 162, 235)",
            colorOk: "rgb(40, 167, 69)",
            colorWarn: "rgb(220, 53, 69)",
      }),
      methods: {
          async getDistance() {
              const r = await axios.get('/api/distance/');
              return r.data.value;  // FIXME
          },
          async update() {
              var dist = await this.getDistance();
              this.chart.data.datasets[0].data.pop();
              this.chart.data.datasets[0].data.pop();
              this.chart.data.datasets[0].data.push(dist);
              this.chart.data.datasets[0].data.push(this.maxDistance - dist);
              if (dist > this.minDistance) {
                  this.chart.data.datasets[0].backgroundColor[0] = this.colorOk;
              } else {
                  this.chart.data.datasets[0].backgroundColor[0] = this.colorWarn;
              }
              this.chart.update();
              this.distance = dist;
          }
      },
      async mounted() {
            this.distance = await this.getDistance();
            this.chart = new Chart(document.getElementById('dist-gauge'), {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [this.distance, this.maxDistance - this.distance],
                        backgroundColor: [
                            this.colorOk,
                            this.colorBg,
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

            this.chart.options.animation.duration = 0;
            setInterval(() => {
                    this.update();
                },
                this.refresh_interval
            );
      } // mounted
};


