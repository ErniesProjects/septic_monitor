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
            var dists = await this.getDistances(); // FIXME - update chart
        }
    },
    async mounted() {
        this.distances = await this.getDistances();        
        this.chart = new Chart(document.getElementById('dist-hourly'), {
            type: 'line',
            data: {                
                datasets: [{
                    data: this.distances,
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

        //this.chart.options.animation.duration = 0;
        //setInterval(() => {this.update();},   this.refresh_interval);
    } // mounted
};


