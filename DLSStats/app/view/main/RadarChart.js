Ext.define("DLSStats.view.main.RadarChart", {
  extend: "Ext.Component",
  xtype: "radarchart",

  config: {
    players: [],
  },

  renderTpl: ['<canvas id="{canvasId}" width="350" height="350"></canvas>'],

  renderSelectors: {
    canvasEl: "canvas",
  },

  beforeRender: function () {
    this.canvasId = Ext.id(null, "radar-canvas-");
    this.callParent(arguments);
  },

  onRender: function () {
    this.callParent(arguments);
    this.drawChart();
  },

  updatePlayers: function (newPlayers) {
    this.players = Ext.isArray(newPlayers) ? newPlayers : [];
    this.drawChart();
  },

  drawChart: function () {
    if (!this.rendered || !this.canvasEl || !this.players.length) {
      return;
    }
    if (typeof Chart === "undefined") {
      console.warn("Chart.js chưa được load");
      return;
    }
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    var ctx = this.canvasEl.dom.getContext("2d");

    var colors = ["rgba(54, 162, 235, 0.2)", "rgba(255, 99, 132, 0.2)"];
    var borderColors = ["rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)"];

    var datasets = Ext.Array.map(this.players, function (p, index) {
      return {
        label: p.fname + " " + p.lname,
        data: [
          parseInt(p.spe) || 0,
          parseInt(p.acc) || 0,
          parseInt(p.sta) || 0,
          parseInt(p.str) || 0,
          parseInt(p.con) || 0,
          parseInt(p.pas) || 0,
          parseInt(p.sho) || 0,
          parseInt(p.tac) || 0,
        ],
        backgroundColor: colors[index % colors.length],
        borderColor: borderColors[index % borderColors.length],
        borderWidth: 2,
        pointBackgroundColor: borderColors[index % borderColors.length],
      };
    });

    this.chartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: ["SPE", "ACC", "STA", "STR", "CON", "PAS", "SHO", "TAC"],
        datasets: datasets,
      },
      options: {
        responsive: false,
        scales: {
          r: {
            min: 0,
            max: 100,
            ticks: {
              stepSize: 20,
              color: "#666",
            },
            pointLabels: {
              color: "#333",
              font: {
                size: 14,
              },
            },
            grid: {
              color: "#ccc",
            },
          },
        },
        plugins: {
          legend: {
            labels: { color: "#000" },
          },
        },
      },
    });
  },

  onDestroy: function () {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
    this.callParent(arguments);
  },
});
