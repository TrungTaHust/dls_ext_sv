Ext.define("DLSStats.view.main.Main", {
  extend: "Ext.container.Viewport",
  xtype: "app-main",
  layout: "fit",

  requires: [
    "DLSStats.view.main.MainSearch",
    "DLSStats.view.main.Compare",
    "DLSStats.view.main.Temp",
    "DLSStats.view.main.SpecialPlayers",
    "DLSStats.view.main.PlayerDevelopment",
    "DLSStats.view.main.About",
    "DLSStats.view.main.FAQ",
  ],

  items: [
    {
      xtype: "tabpanel",
      items: [
        {
          title: "Search",
          xtype: "dls-mainsearch",
          reference: "dls-mainsearch",
        },
        {
          title: "Compare",
          xtype: "dls-compare",
          reference: "compare",
        },
        {
          title: "Special Players",
          xtype: "dls-specialplayers",
          reference: "specialplayers",
        },
        {
          title: "Player Development",
          xtype: "dls-playerdevelopment",
          reference: "playerdevelopment",
        },
        {
          title: "FAQ",
          xtype: "dls-faq",
          reference: "faq",
        },
        {
          title: "About",
          xtype: "about",
          reference: "about",
        },
      ],
    },
  ],
});
