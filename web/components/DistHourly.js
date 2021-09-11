export default Vue.component('DistHourly', {
    template: `
    <div>
        <canvas id="dist-hourly"></canvas>
    </div>
    `,
    data: () => ({
        distances: [],
        chart: null,
        refresh_interval: 2000,
        minDistance: 25,  // FIXME
        colorLine: "rgb(54, 162, 235)",
		colorWarn: "rgb(220, 53, 69)",
    }),
    methods: {
        async getDistances() {
            const r = await axios.get('/api/distance/hour/');
            return r.data;
        },
        async update() {
            var dists = await this.getDistances();
            this.chart.data.datasets[0].data = dists;
			this.chart.update();
            this.distances = dists;
        }
    },
    async mounted() {
        this.distances = await this.getDistances();
        this.chart = new Chart(document.getElementById('dist-hourly'), {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: "Hourly Distance",
                        data: this.distances,
                        borderColor: this.colorLine,
                        tension: 0.1
                    },
                    {
                        label: "Min Safe",
                        fill: true,
                        data: [{x: this.distances[0].x, y: this.minDistance}, {x: this.distances.at(-1).x, y: this.minDistance}],
                        borderColor: this.colorWarn,                        
                    }
                ],
            },
            options: {
                scales: {
                    xAxis: {
                        type: 'time',
                    }
                },
                //plugins: {
                //    annotation: {
                //        annotations: {
                //              warnAnnotation,
                //        }
                //    }
                //},
            }
        });  // this.chart

        this.chart.options.animation.duration = 0;
        setInterval(() => {this.update();},   this.refresh_interval);
    } // mounted
});


