export default Vue.component('Status', {	
	template: `
    <v-card shaped outlined height="100%">
        <v-card-title>Status</v-card-title>
        <v-card-text>
            <v-alert type="error">FOO</v-alert>
            <v-alert type="success">Last Update: {{ status.lastUpdate.replace('T', ' @ ') }}</v-alert>
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
