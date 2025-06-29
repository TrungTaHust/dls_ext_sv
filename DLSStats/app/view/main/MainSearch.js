Ext.define("DLSStats.view.main.MainSearch", {
  extend: "Ext.container.Container",
  xtype: "dls-mainsearch",
  layout: "fit",
  scrollable: true,

  style: {
    backgroundImage: 'url("./resources/background.jpg")',
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
  },

  requires: [
    "DLSStats.view.main.SearchForm",
    "DLSStats.view.main.PlayerGrid",
    "DLSStats.view.main.PlayerDetails",
    "DLSStats.view.main.PlayerController",
  ],

  controller: "player",
  referenceHolder: true,

  viewModel: {
    data: {
      hasPrev: false,
      hasNext: false,
    },
    stores: {
      players: {
        fields: ["fname", "lname", "pos", "rate", "version", "id"],
        data: [],
      },
    },
  },

  layout: {
    type: "vbox",
    align: "stretch",
  },

  items: [
    //Search Form
    {
      xtype: "dls-searchform",
      reference: "dls-searchform",
    },
    //Players
    {
      xtype: "container",
      reference: "responsiveContent",
      layout: {
        type: "hbox",
        pack: "center",
      },
      responsiveConfig: {
        "width < 600": {
          layout: {
            type: "vbox",
            align: "stretch",
          },
        },
        "width >= 600": {
          layout: {
            type: "hbox",
            pack: "center",
          },
        },
      },
      defaults: {
        margin: 20,
        flex: 1,
      },
      items: [
        //Player Grid
        {
          xtype: "dls-playergrid",
          minWidth: 300,
          maxWidth: 520,
          responsiveConfig: {
            "width < 600": {
              maxWidth: null,
            },
          },
        },
        //Player Detail
        {
          xtype: "dls-playerdetails",
          reference: "playerdetails",
          minWidth: 280,
          maxWidth: 400,
          responsiveConfig: {
            "width < 600": {
              maxWidth: null,
            },
          },
        },
      ],
    },
  ],
});
