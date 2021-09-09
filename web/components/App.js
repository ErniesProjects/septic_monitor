import DistGuage from './DistGuage.js';

export default {
    name: 'App',
    template: `
        <v-container>
            <div>
                {{ message }}
            </div>
            <DistGuage></DistGuage>
        </v-container>
    `,
    components: {
        DistGuage,
    },
    data() {
        return {
            message: "HELLO",
        };
    },
};
