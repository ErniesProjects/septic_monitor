export default Vue.component('LevelGauge', {
	template: `
	<div>
		<div class="text-center text--secondary"><h2>Water Level</h2></div>
        <div class="text-center text--secondary"><h3>{{ absLevel }} cm from sensor</h3></div>
        <div class="text-center" style="color:#999">{{ lastUpdate }}</div>
		<div class="text-center" style="color:#999">(warn > {{ maxLevel }})</div>
		<canvas id="level-gauge"></canvas>
	</div>
	`,
	data: () => ({
		maxLevel: -5,  // FIXME
		level: null,
        lastUpdate: null,
        lowestLevel: -40,  // FIXME
		chart: null,
		refresh_interval: 2000,
		colorBg: "rgb(54, 162, 235)",
		colorOk: "rgb(54, 162, 235)",
		colorWarn: "rgb(220, 53, 69)",
	}),
    computed: {
        absLevel: function() {
            return Math.abs(this.level);
        }
    },
	methods: {
		async getLevel() {
			var r = await axios.get('/api/level/');
			return r.data;  // wait to refresh gauge before set data attr
		},
		async update() {
			var l = await this.getLevel();
            var level = l.value;
			this.chart.data.datasets[0].data = [];
			this.chart.data.datasets[0].data.push([this.lowestLevel, level]);
			if (level > this.maxLevel) {
			  this.chart.data.datasets[0].backgroundColor = this.colorWarn;
			} else {
			  this.chart.data.datasets[0].backgroundColor = this.colorOk;
			}
			this.chart.update();
			this.level = level;
            this.lastUpdate = l.timestamp;
		}
	},
	async mounted() {
		var l = await this.getLevel();
        this.level = l.value;
        this.lastUpdate = l.timestamp;
		this.chart = new Chart(document.getElementById('level-gauge'), {
			type: 'bar',
			data: {
                labels: ["Level"],
				datasets: [{
					data: [[this.lowestLevel, this.level]],
					backgroundColor: this.colorOk,
				}],
			},
			options: {
                plugins: {
                    legend: {
                        display: false,
                    }
                },
                scales: {
                    yAxes: [{
                        ticks: {min: -40, max: 0}
                    }]
                }
            }
		});  // this.chart

		this.chart.options.animation.duration = 0;
		setInterval(this.update, this.refresh_interval);
	} // mounted
});
