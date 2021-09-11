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
        minDistance: -5,  // FIXME
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
            this.chart.data.datasets[1].data = [{x: this.distances[0].x, y: this.minDistance}, {x: this.distances.at(-1).x, y: this.minDistance}],
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
                        label: "Hourly Level",
                        data: this.distances,
                        borderColor: this.colorLine,
                        tension: 0.1
                    },
                    {
                        label: "Max Safe",
                        fill: "start",                        
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
            }
        });  // this.chart

        this.chart.options.animation.duration = 0;
        setInterval(() => {this.update();},   this.refresh_interval);
    } // mounted
});


