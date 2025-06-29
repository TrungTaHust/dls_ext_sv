Ext.define("DLSStats.view.main.PlayerGrid", {
  extend: "Ext.panel.Panel",
  xtype: "dls-playergrid",

  layout: "fit",
  bodyPadding: 5,
  title: "Search Results",

  responsiveConfig: {
    "width < 600": {
      maxWidth: null,
    },
    "width >= 600": {
      maxWidth: 520,
    },
  },

  items: [
    {
      xtype: "grid",
      reference: "playerList",
      bind: {
        store: "{players}",
      },
      columnLines: true,
      rowLines: true,
      scrollable: true,

      columns: [
        {
          text: "Name",
          dataIndex: "full_name",
          flex: 2,
          minWidth: 150,
          sortable: false,
          menuDisabled: true,
          renderer: function (v, meta, rec) {
            meta.style = "font-weight: bold";
            return rec.get("fname") + " " + rec.get("lname");
          },
        },
        {
          text: "ID",
          dataIndex: "id",
          align: "center",
          flex: 1,
          minWidth: 80,
          sortable: false,
          menuDisabled: true,
          renderer: function (v, meta, rec) {
            meta.style = "font-weight: bold";
            return rec.get("id");
          },
        },
        {
          text: "Position",
          dataIndex: "pos",
          align: "center",
          flex: 1,
          minWidth: 80,
          sortable: false,
          menuDisabled: true,
          renderer: function (value, meta) {
            var pos = (value || "").toLowerCase();
            var bgColor = "black";
            var color = "black";

            if (["cf", "ss", "lw", "rw"].indexOf(pos) >= 0) {
              bgColor = "red";
            } else if (
              ["cm", "am", "dm", "lm", "rm", "lwb", "rwb"].indexOf(pos) >= 0
            ) {
              bgColor = "yellow";
            } else if (["cb", "lb", "rb"].indexOf(pos) >= 0) {
              bgColor = "lime";
            } else if (pos === "gk") {
              bgColor = "cyan";
            }

            meta.style =
              "background-color: " +
              bgColor +
              "; color: " +
              color +
              "; font-weight: bold; text-align: center";

            return value ? value.toUpperCase() : "";
          },
        },
        {
          text: "Rating",
          dataIndex: "rate",
          align: "center",
          flex: 1,
          minWidth: 80,
          sortable: false,
          menuDisabled: true,
          renderer: function (v, meta, rec) {
            meta.style = "font-weight: bold";
            return rec.get("rate");
          },
        },
      ],

      listeners: {
        itemclick: "onPlayerSelect",
      },
    },
  ],

  bbar: {
    xtype: "toolbar",
    items: [
      "->",
      {
        text: "Back",
        handler: "onBack",
        style: {
          backgroundColor: "green",
        },
        bind: { disabled: "{!hasPrev}" },
        listeners: {
          afterrender: function (btn) {
            var inner = btn.el.dom.querySelector(".x-btn-inner");
            if (inner) inner.style.color = "black";
          },
        },
      },
      {
        text: "Next",
        handler: "onNext",
        style: {
          backgroundColor: "green",
          color: "black",
        },
        bind: { disabled: "{!hasNext}" },
        listeners: {
          afterrender: function (btn) {
            var inner = btn.el.dom.querySelector(".x-btn-inner");
            if (inner) inner.style.color = "black";
          },
        },
      },
      "->",
    ],
  },
});
