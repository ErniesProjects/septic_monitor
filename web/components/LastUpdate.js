export default Vue.component('LastUpdate', {	
	template: `
	<div class="text-center">
		<div class="font-weight-bold text-h4 text--secondary">Last Update</div>
		<div class="font-weight-bold text-h4 text--secondary">{{ lastupdate.date }}</div>
		<div class="font-weight-bold text-h4 text--secondary">{{ lastupdate.time }}</div>
	</div>
	`,
	data: () => ({
		refresh_interval: 2000,
		lastupdate: {
			date: null,
			time: null
		},
	}),
	methods: {
	  async getLastUpdate() {
		  var r = await axios.get('/api/lastupdate/');
		  this.lastupdate =  {
			  date: r.data.split("T")[0],
			  time: r.data.split("T")[1]				
		  }
	  },
	},
	async mounted() {
		await this.getLastUpdate();
		setInterval(() => {
				this.getLastUpdate();
			},
			this.refresh_interval
		);
	} // mounted
});
