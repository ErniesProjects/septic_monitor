export default Vue.component('LevelHour', {
    template: `
    <div>
        <canvas id="level-hour"></canvas>
    </div>
    `,
    data: () => ({
        levels: [],
        chart: null,
        refresh_interval: 2000,
        maxLevel: -5,  // FIXME
        colorLine: "rgb(54, 162, 235)",
		colorWarn: "rgb(220, 53, 69)",
    }),
    methods: {
        async getLevels() {
            const r = await axios.get('/api/level/hour/');
            return r.data;
        },
        async update() {
            var levels = await this.getLevels();
            this.chart.data.datasets[0].data = levels;
            this.chart.data.datasets[1].data = [{x: this.levels[0].x, y: this.maxLevel}, {x: this.levels.at(-1).x, y: this.maxLevel}],
            this.chart.data.datasets[2].data = [{x: this.levels[0].x, y: 0}, {x: this.levels.at(-1).x, y: 0}],			
            this.chart.update();
            this.levels = levels;
        }
    },
    async mounted() {
        this.levels = await this.getLevels();
        this.chart = new Chart(document.getElementById('level-hour'), {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: "Last Hour Levels",
                        data: this.levels,
                        borderColor: this.colorLine,
                        tension: 0.1,
                        fill: "start",
                    },
                    {
                        label: "Max Safe",
                        fill: "start",                        
                        data: [{x: this.levels[0].x, y: this.maxLevel}, {x: this.levels.at(-1).x, y: this.maxLevel}],
                        borderColor: this.colorWarn,                        
                    },
                    {
                        label: "Sensor",                        
                        data: [{x: this.levels[0].x, y: 0}, {x: this.levels.at(-1).x, y: 0}],
                        borderColor: "dimgray",                        
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


