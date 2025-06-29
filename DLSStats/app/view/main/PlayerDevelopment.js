Ext.define("DLSStats.view.main.PlayerDevelopment", {
  extend: "Ext.container.Container",
  xtype: "dls-playerdevelopment",

  layout: {
    type: "vbox",
    align: "center",
    pack: "start",
  },

  padding: 20,
  scrollable: true,

  style: {
    backgroundImage: 'url("./resources/background.jpg")',
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
  },

requires: [
  "Ext.chart.CartesianChart",
  "Ext.chart.axis.Category",
  "Ext.chart.axis.Numeric",
  "Ext.chart.series.Line",
  "Ext.chart.legend.Legend",
  "Ext.chart.interactions.ItemHighlight",
  "Ext.data.Store"
],


  controller: {
    async onLoadPlayerData() {
      const view = this.getView();
      const playerIdField = view.lookupReference("playerIdField");
      const playerId = playerIdField.getValue();
      const chart = view.lookupReference("playerChart");

      if (!playerId) {
        Ext.Msg.alert("Missing ID", "You must enter an ID!");
        return;
      }

      try {
        const response = await fetch("https://trungta-hust-dls24.vercel.app/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            criteria: {
              id: playerId,
            },
          }),
        });

        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
          Ext.Msg.alert("Not found!", "This ID has no data! Please try again!");
          return;
        }

        const filteredData = data
          .filter((item) => item.version && item.rate !== undefined)
          .map((item) => {
            return {
              uid: `${item.id}_${item.version}`,
              version: String(item.version),
              rate: item.rate,
              spe: item.spe,
              acc: item.acc,
              sta: item.sta,
              str: item.str,
              con: item.con,
              pas: item.pas,
              sho: item.sho,
              tac: item.tac,
            };
          })
          .sort((a, b) => a.version.localeCompare(b.version));

        const newStore = Ext.create("Ext.data.Store", {
          fields: [
            "uid",
            "version",
            "rate",
            "spe",
            "acc",
            "sta",
            "str",
            "con",
            "pas",
            "sho",
            "tac",
          ],
          idProperty: "uid",
          data: filteredData,
        });

        chart.setStore(newStore);
      } catch (error) {
        Ext.Msg.alert("Error", "Server down. Please try again!");
      }
    },
  },

  items: [
    //ID
    {
      xtype: "textfield",
      reference: "playerIdField",
      emptyText: "Enter player's ID (Example: 8335)",
      width: 300,
      margin: "0 0 10 0",
    },
    //Search Button
    {
      xtype: "button",
      text: "Search",
      width: 150,
      handler: "onLoadPlayerData",
      margin: "0 0 20 0",
    },
    //Chart
    {
      xtype: "cartesian",
      reference: "playerChart",
      width: 700,
      height: 500,
      insetPadding: 40,
      store: {
        fields: [
          "uid",
          "version",
          "rate",
          "spe",
          "acc",
          "sta",
          "str",
          "con",
          "pas",
          "sho",
          "tac",
        ],
        idProperty: "uid",
      },
      legend: {
        docked: "right",
        listeners: {
          legenditemclick: function (legend, item) {
            var chart = legend.getChart();
            var seriesList = chart.getSeries();

            Ext.each(seriesList, function (series) {
              if (series === item.series) {
                series.setStyle({
                  opacity: 1,
                  strokeOpacity: 1,
                });
                series.show();
              } else {
                series.setStyle({
                  opacity: 0.2,
                  strokeOpacity: 0.2,
                });
                series.show();
              }
            });
            return false;
          },
        },
      },
      axes: [
        {
          type: "numeric",
          position: "left",
          minimum: 0,
          maximum: 100,
        },
        {
          type: "category",
          position: "bottom",
          title: "Version",
          fields: ["version"],
        },
      ],
      series: [
        "rate",
        "spe",
        "acc",
        "sta",
        "str",
        "con",
        "pas",
        "sho",
        "tac",
      ].map(function (field) {
        return {
          type: "line",
          xField: "version",
          yField: field,
          title: field.toUpperCase(),
          marker: {
            radius: 3,
          },
          highlight: {
            size: 6,
            radius: 6,
          },
          style: {
            lineWidth: 2,
            opacity: 1,
          },
        };
      }),
    },
  ],
});
