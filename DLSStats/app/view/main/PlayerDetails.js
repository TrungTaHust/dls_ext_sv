Ext.define("DLSStats.view.main.PlayerDetails", {
  extend: "Ext.panel.Panel",
  xtype: "dls-playerdetails",
  reference: "playerdetails",
  title: "Player Details",
  scrollable: true,
  bodyPadding: 10,
  referenceHolder: true,

  layout: {
    type: "vbox",
    align: "stretch",
  },

  items: [
    // Header
    {
      xtype: "container",
      reference: "headerContainer",
      style: {
        backgroundColor: "#f0f0f0",
      },
      items: [
        {
          xtype: "component",
          reference: "name",
          html: '<h2 style="text-align:center;">No player selected</h2>',
        },
      ],
    },
    // Basic info
    {
      xtype: "container",
      reference: "basicInfoContainer",
      layout: {
        type: "hbox",
        align: "stretch",
      },
      responsiveConfig: {
        "width < 600": {
          layout: {
            type: "vbox",
            align: "stretch",
          },
        },
      },

      defaults: {
        xtype: "container",
        layout: "vbox",
        flex: 1,
        padding: "0 10",
        defaults: {
          xtype: "component",
          margin: "8 0",
        },
      },

      items: [
        {
          items: [
            { reference: "id", html: "ID: " },
            { reference: "prc", html: "Price: " },
            { reference: "nat", html: "Nationality: " },
            { reference: "club", html: "Club: " },
            { reference: "pos", html: "Position: " },
          ],
        },
        {
          items: [
            { reference: "version", html: "Version: " },
            { reference: "foot", html: "Leg: " },
            { reference: "rate", html: "Rating: " },
            { reference: "hgt", html: "Height: " },
          ],
        },
      ],
    },
    // Stats
    {
      xtype: "container",
      reference: "statsContainer",
      layout: {
        type: "vbox",
        align: "center",
      },
      margin: "10 0",

      defaults: {
        width: "100%",
        //maxWidth: 500,
        margin: "5 0",
      },

      items: [
        {
          xtype: "container",
          layout: {
            type: "hbox",
            align: "stretch",
          },
          responsiveConfig: {
            "width < 600": {
              layout: {
                type: "vbox",
                align: "stretch",
              },
            },
          },
          defaults: {
            xtype: "component",
            flex: 1,
            padding: 5,
            margin: 5,
            style:
              "text-align:center; border: 1px solid #ccc; font-weight: bold;",
          },
          items: [
            { reference: "spe", html: "SPE: ?" },
            { reference: "acc", html: "ACC: ?" },
            { reference: "sta", html: "STA: ?" },
            { reference: "str", html: "STR: ?" },
          ],
        },
        {
          xtype: "container",
          layout: {
            type: "hbox",
            align: "stretch",
          },
          responsiveConfig: {
            "width < 600": {
              layout: {
                type: "vbox",
                align: "stretch",
              },
            },
          },
          defaults: {
            xtype: "component",
            flex: 1,
            padding: 5,
            margin: 5,
            style:
              "text-align:center; border: 1px solid #ccc; font-weight: bold;",
          },
          items: [
            { reference: "con", html: "CON: ?" },
            { reference: "pas", html: "PAS: ?" },
            { reference: "sho", html: "SHO: ?" },
            { reference: "tac", html: "TAC: ?" },
          ],
        },
      ],
    },
  ],

  updatePlayer: function (player) {
    if (!player || !player.lname) {
      this.lookupReference("name").setHtml("<h2>No player selected</h2>");
      return;
    }

    function getStatColor(val) {
      val = parseInt(val, 10);
      if (isNaN(val)) return "lightgray";
      if (val >= 90) return "cyan";
      if (val >= 80) return "lime";
      if (val >= 70) return "yellow";
      if (val >= 60) return "orange";
      if (val >= 50) return "crimson";
      return "red";
    }

    var me = this;

    function setStatsColor(ref, val, prefix) {
      var cmp = me.lookupReference(ref);
      if (cmp) {
        cmp.setHtml(prefix + (val != null ? val : "?"));
        var color = getStatColor(val);
        cmp.setStyle({
          "background-color": "black",
          color: color,
        });
      }
    }

    function set(ref, val, prefix) {
      var cmp = me.lookupReference(ref);
      if (cmp) {
        cmp.setHtml("<b>" + prefix + (val != null ? val : "?") + "</b>");
      }
    }

    // Header
    var rate = parseInt(player.rate, 10);
    var bgColor = "grey";
    if (rate >= 80) bgColor = "gold";
    else if (rate >= 70) bgColor = "aqua";

    var headerContainer = this.lookupReference("headerContainer");
    if (headerContainer) {
      headerContainer.setStyle("background-color", bgColor);
    }

    this.lookupReference("name").setHtml(
      "<h2>" + player.fname + " " + player.lname + "</h2>"
    );

    // Basic Info
    set("prc", player.prc, "Price: ");
    set("nat", player.nat, "Nationality: ");
    set("club", player.club, "Club: ");
    set("pos", player.pos, "Position: ");
    set("foot", player.foot, "Leg: ");
    set("rate", player.rate, "Rating: ");
    set("hgt", player.hgt, "Height: ");
    set("version", player.version, "Version: ");
    set("id", player.id, "ID: ");

    // Stats
    setStatsColor("spe", player.spe, "SPE: ");
    setStatsColor("acc", player.acc, "ACC: ");
    setStatsColor("sta", player.sta, player.pos === "GK" ? "GKR: " : "STA: ");
    setStatsColor("str", player.str, "STR: ");
    setStatsColor("con", player.con, "CON: ");
    setStatsColor("pas", player.pas, "PAS: ");
    setStatsColor("sho", player.sho, player.pos === "GK" ? "GKH: " : "SHO: ");
    setStatsColor("tac", player.tac, "TAC: ");

    var radarChart = this.lookupReference("radarChartCmp");
    if (radarChart) {
      radarChart.updatePlayer(player);
    }
  },
});
