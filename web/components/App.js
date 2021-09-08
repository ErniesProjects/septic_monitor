import DistGuage from './DistGuage.js';

export default {
  name: 'App',
  template: `
    <div>
      {{ message }}
    </div>
    <DistGuage></DistGuage>
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
