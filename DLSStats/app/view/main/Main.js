Ext.define("DLSStats.view.main.Main", {
  extend: "Ext.container.Viewport",
  xtype: "app-main",
  layout: "fit",

  requires: [
    "DLSStats.view.main.MainSearch",
    "DLSStats.view.main.Compare",
    "DLSStats.view.main.Favorites",
    "DLSStats.view.main.BestXI",
    "DLSStats.view.main.TeamShowcase",
    "DLSStats.view.main.SpecialPlayers",
    "DLSStats.view.main.Upgrade",
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
          title: "Favorites",
          xtype: "dls-favorites",
          reference: "favorites",
        },
        {
          title: "Best XI",
          xtype: "dls-bestxi",
          reference: "bestxi",
        },
        {
          title: "Team Showcase",
          xtype: "dls-teamshowcase",
          reference: "teamshowcase",
        },
        {
          title: "Special Players",
          xtype: "dls-specialplayers",
          reference: "specialplayers",
        },
        {
          title: "Upgrade Sim",
          xtype: "dls-upgrade",
          reference: "upgrade",
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