import LevelGauge from './components/LevelGauge.js';
import LastUpdate from './components/LastUpdate.js';
import LevelChart from './components/LevelChart.js';
import AmpGauge from './components/AmpGauge.js';
import SettingsDialog from './components/SettingsDialog.js';


Vue.use(Vuex);
Vue.use(Vuetify);


const store = new Vuex.Store({
    state: {
        maxLevel: null,
    },
    mutations: {
        setMaxLevel(state, level) {
            state.maxLevel = level;
        }
    }
})


new Vue({
    el: "#app",
    store: store,
    vuetify: new Vuetify(),
    template: `
        <v-app>
          <v-main>
            <v-container fluid>

               <v-toolbar src="/background.jpg">
                  <v-toolbar-title class="ml-4">SepMon</v-toolbar-title>
                  <v-spacer></v-spacer>
                  <v-dialog v-model="settingsOpen" fullscreen hide-overlay>
                    <template v-slot:activator="{on, attrs}">
                      <v-btn icon v-bind="attrs" v-on="on">
                          <v-icon>mdi-dots-vertical</v-icon>
                      </v-btn>
                    </template>
                    <SettingsDialog :settings-open.sync="settingsOpen"></SettingsDialog>
                  </v-dialog>
                </v-toolbar>

                <v-row align="top" justify="center" class="mt-8">
                    <v-col>
                        <v-card elevation="2" shaped class="py-8">
                            <LastUpdate></LastUpdate>
                        </v-card>
                    </v-col>
                    <v-col><LevelGauge></LevelGauge></v-col>
                    <v-col><AmpGauge></AmpGauge></v-col>
                </v-row>

                <div class="mt-12 mb-6 text-center text--secondary"><h2>Tank Levels</h2></div>

                <div>
                    <v-tabs v-model="tab">
                        <v-tab>Hour</v-tab>
                        <v-tab>Day</v-tab>
                        <v-tab>Week</v-tab>
                        <v-tab>Month</v-tab>
                    </v-tabs>

                    <v-tabs-items v-model="tab">
                        <v-tab-item><LevelChart duration="hour"></LevelChart></v-tab-item>
                        <v-tab-item><LevelChart duration="day"></LevelChart></v-tab-item>
                        <v-tab-item><LevelChart duration="week"></LevelChart></v-tab-item>
                        <v-tab-item><LevelChart duration="month"></LevelChart></v-tab-item>
                    </v-tabs-items>

                </div>

            </v-container>
          </v-main>
        </v-app>
    `,
    components: {
        SettingsDialog,
        LastUpdate,
        LevelGauge,
        LevelChart,
        AmpGauge,
    },
    data() {
        return {
            settingsOpen: false,
            tab: null,
        };
    },
});
