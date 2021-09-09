//import Vue from 'vue';
//import Vuetify from 'vuetify';

import DistGuage from './components/DistGuage.js';
import AmpGuage from './components/AmpGuage.js';

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
                    <v-col><DistGuage></DistGuage></v-col>
                    <v-col><AmpGuage></AmpGuage></v-col>
                </v-row>
            </v-container>
          </v-main>
        </v-app>
    `,
    components: {
        AmpGuage,
        DistGuage,
    },
    data() {
        return {
            message: "HELLO",
        };
    },
});
