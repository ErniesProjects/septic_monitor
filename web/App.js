import LevelGauge from './components/LevelGauge.js';
import LastUpdate from './components/LastUpdate.js';
import LevelChart from './components/LevelChart.js';

Vue.use(Vuetify);

new Vue({
    el: "#app",
    vuetify: new Vuetify(),
    template: `
        <v-app>
          <v-main>
            <v-container>

               <v-toolbar color="blue">
                  <v-toolbar-title class="ml-4">Septic Monitor</v-toolbar-title>
                  <v-spacer></v-spacer>
                  <v-btn icon>
                      <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </v-toolbar>

                <v-row align="center" justify="center" class="mt-8">
                    <v-col><LastUpdate></LastUpdate></v-col>
                    <v-col><LevelGauge></LevelGauge></v-col>
                </v-row>

                <div class="mt-12 mb-6 text-center text--secondary"><h2>Water Level Charts</h2></div>
                
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
        LastUpdate,
        LevelGauge,
        LevelChart,
    },
    data() {
        return {
            tab: null,
        };
    },
});
