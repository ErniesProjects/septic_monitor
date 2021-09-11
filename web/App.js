import LevelGauge from './components/LevelGauge.js';
import LastUpdate from './components/LastUpdate.js';
import LevelHour from './components/LevelHour.js';

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
                    <v-col><LevelGauge></LevelGauge></v-col>
                </v-row>
                <v-row>
                    <v-col cols="12"><LevelHour></LevelHour></v-col>
                </v-row>
            </v-container>
          </v-main>
        </v-app>
    `,
    components: {
        LastUpdate,
        LevelGauge,
        LevelHour,
    },
    data() {
        return {
            message: "HELLO",
        };
    },
});
