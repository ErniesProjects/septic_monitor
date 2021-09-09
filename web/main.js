import DistGauge from './components/DistGauge.js';
import AmpGauge from './components/AmpGauge.js';

Vue.use(Vuetify);

new Vue({
    el: "#app",
    vuetify: new Vuetify(),
    template: `
        <v-app>
          <v-main>
            <v-container>
                <div>
                    {{ message }}
                </div>
                <v-row>
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
    },
    data() {
        return {
            message: "HELLO",
        };
    },
});
