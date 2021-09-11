export default {
    name: 'DistHourly',
    template: `
    <div>
        <canvas id="dist-hourly"></canvas>
    </div>
    `,
    data: () => ({
        distances: [],
        chart: null,
        refresh_interval: 2000,
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
                datasets: [{
                    label: "Hourly Distance",
                    data: this.distances,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }],
            },
            options: {
                scales: {
                    xAxis: {
                        type: 'time',
                    }
                }
            }
        });  // this.chart

        this.chart.options.animation.duration = 0;
        setInterval(() => {this.update();},   this.refresh_interval);
    } // mounted
};


