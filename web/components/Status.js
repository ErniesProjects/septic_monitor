export default Vue.component('Status', {	
	template: `
    <v-card shaped outlined>
        <v-card-title>Status</v-card-title>
        <v-card-text>
            <span><b>Last Update:</b> {{ status.lastUpdate }}</span>
        </v-card-text>
    </v-card>
	`,
	data: () => ({
		refresh_interval: 2000,
		status: {},
	}),
	methods: {
	  async getStatus() {
		  var r = await axios.get('/api/status/');
		  this.status =  r.data;
	  },
	},
	async mounted() {
		await this.getStatus();
		setInterval(() => {
				this.getStatus();
			},
			this.refresh_interval
		);
	} // mounted
});
