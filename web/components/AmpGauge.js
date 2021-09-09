export default {
  name: 'AmpGauge',
  template: `
    <div>
        <canvas id="amp-gauge"></canvas>
    </div>
  `,
  data: () => ({
        cpuloads: [],
      }),
  mounted() {
        var dg = document.getElementById('amp-gauge');
        new Chart(dg, {
          type: 'doughnut',
          data: {
            datasets: [{
              data: [90, 10]
            }],
          },
          options: {
            title: {
              display: true,
              text: "dist (cm)",
              fontSize: 22
            },
            tooltips: {
              enabled: false
            },
            hover: {
              mode: null
            }
          }
        });
  } // mounted
};


