Ext.define("DLSStats.view.main.SearchForm", {
  extend: "Ext.form.Panel",
  xtype: "dls-searchform",

  bodyPadding: 10,
  bodyStyle: "background-color: rgba(255, 255, 255, 0);",

  layout: {
    type: "vbox",
    align: "center",
    pack: "center",
  },
  defaults: {
    margin: 10,
    flex: 1,
    minWidth: 120,
  },

  items: [
    // Search form inputs container, responsive layout
    {
      xtype: "container",
      width: "100%",
      layout: {
        type: "hbox",
        align: "middle",
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
            align: "middle",
            pack: "center",
          },
        },
      },
      defaults: {
        margin: "0 10",
        flex: 1,
        minWidth: 120,
      },
      items: [
        //ID
        {
          xtype: "textfield",
          name: "id",
          emptyText: "Enter player's ID (Example: 8335)",
          maskRe: /[0-9]/,
          regex: /^[0-9]{0,4}$/,
          regexText: "ID chỉ được chứa tối đa 4 chữ số",
          enforceMaxLength: true,
          maxLength: 4,
        },
        //Version
        {
          xtype: "combo",
          name: "version",
          emptyText: "Version",
          store: ["20253", "20252", "20251", "20242", "20241", "20231"],
          queryMode: "local",
          editable: false,
          value: "20253",
        },
        //Name
        {
          xtype: "textfield",
          name: "name",
          emptyText: "Name",
        },
        //Nationality
        {
          xtype: "combo",
          name: "nat",
          emptyText: "Nationality",
          store: { type: "nationsstore" },
          queryMode: "local",
          displayField: "name",
          valueField: "name",
          typeAhead: true,
          minChars: 1,
          forceSelection: false,
        },
        //Club
        {
          xtype: "combo",
          name: "club",
          emptyText: "Club",
          store: { type: "clubsstore" },
          queryMode: "local",
          displayField: "name",
          valueField: "name",
          typeAhead: true,
          minChars: 1,
          forceSelection: false,
        },
        //Position
        {
          xtype: "combo",
          name: "pos",
          emptyText: "Position",
          store: [
            "CF",
            "LW",
            "RW",
            "SS",
            "AM",
            "CM",
            "DM",
            "LM",
            "RM",
            "LWB",
            "RWB",
            "LB",
            "RB",
            "CB",
            "GK",
          ],
          queryMode: "local",
          editable: false,
        },
        //Foot
        {
          xtype: "combo",
          name: "foot",
          emptyText: "Foot",
          store: ["L", "R", "B"],
          queryMode: "local",
          editable: false,
        },
        //Rating
        {
          xtype: "textfield",
          name: "rate",
          emptyText: "Rating",
        },
      ],
    },
    // Search Button
    {
      xtype: "button",
      text: "Search",
      formBind: true,
      handler: function (btn) {
        const form = btn.up("form");
        const values = form.getValues();
        console.log("Search values:", values);
        form.fireEvent("searchrequest", values);
      },
    },
  ],
});
