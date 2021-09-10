import DistGauge from './components/DistGauge.js';
import AmpGauge from './components/AmpGauge.js';
import LastUpdate from './components/LastUpdate.js';

Vue.use(Vuetify);

new Vue({
    el: "#app",
    vuetify: new Vuetify(),
    template: `
        <v-app>
          <v-main>
            <v-container>
                <v-row align="center" justify="center">
                    <v-col><LastUpdate></LastUpdate></v-col>
                    <v-col><DistGauge></DistGauge></v-col>
                    <v-col><AmpGauge></AmpGauge></v-col>
                </v-row>
            </v-container>
          </v-main>
        </v-app>
    `,
    components: {
        AmpGauge,
        DistGauge,
        LastUpdate,
    },
    data() {
        return {
            message: "HELLO",
        };
    },
});
