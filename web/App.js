import DistGauge from './components/DistGauge.js';
import LastUpdate from './components/LastUpdate.js';
import DistHourly from './components/DistHourly.js';

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
                </v-row>
                <v-row>
                    <v-col cols="12"><DistHourly></DistHourly></v-col>
                </v-row>
            </v-container>
          </v-main>
        </v-app>
    `,
    components: {
        LastUpdate,
        DistGauge,
        DistHourly,
    },
    data() {
        return {
            message: "HELLO",
        };
    },
});
