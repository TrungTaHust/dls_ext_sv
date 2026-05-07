Ext.define("DLSStats.view.main.Compare", {
    extend: "Ext.container.Container",
    xtype: "dls-compare",
    title: "Compare Players",
    scrollable: true,

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    },

    requires: ["DLSStats.view.main.CompareController"],

    controller: "compare",
    referenceHolder: true,

    layout: { type: "vbox", align: "center", pack: "start" },
    padding: 10,

    items: [
        // Input row
        {
            xtype: "container",
            reference: "inputContainer",
            layout: { type: "hbox", pack: "center", align: "middle" },
            margin: "0 0 10 0",
            defaults: { margin: 6 },
            style: { flexWrap: "wrap", rowGap: "4px" },
            items: [
                // Player 1
                { xtype: "textfield", itemId: "player1Id", emptyText: "ID 1", width: 80 },
                { xtype: "combo", itemId: "version1", emptyText: "Ver 1", store: { type: "versionstore" }, displayField: "version", valueField: "version", queryMode: "local", editable: false, value: "20262", width: 100 },
                // Player 2
                { xtype: "textfield", itemId: "player2Id", emptyText: "ID 2", width: 80 },
                { xtype: "combo", itemId: "version2", emptyText: "Ver 2", store: { type: "versionstore" }, displayField: "version", valueField: "version", queryMode: "local", editable: false, value: "20262", width: 100 },
                // Player 3 (hidden by default)
                { xtype: "textfield", itemId: "player3Id", emptyText: "ID 3", width: 80, hidden: true },
                { xtype: "combo", itemId: "version3", emptyText: "Ver 3", store: { type: "versionstore" }, displayField: "version", valueField: "version", queryMode: "local", editable: false, value: "20262", width: 100, hidden: true },
                // Player 4 (hidden by default)
                { xtype: "textfield", itemId: "player4Id", emptyText: "ID 4", width: 80, hidden: true },
                { xtype: "combo", itemId: "version4", emptyText: "Ver 4", store: { type: "versionstore" }, displayField: "version", valueField: "version", queryMode: "local", editable: false, value: "20262", width: 100, hidden: true },
                // Action buttons
                {
                    xtype: "button", reference: "addPlayerBtn", text: "+ Add Player",
                    style: { backgroundColor: "#2980b9", color: "white" },
                    handler: "onAddPlayer",
                },
                {
                    xtype: "button", reference: "removePlayerBtn", text: "- Remove Player",
                    style: { backgroundColor: "#c0392b", color: "white" },
                    hidden: true,
                    handler: "onRemovePlayer",
                },
                {
                    xtype: "button", text: "Compare",
                    style: { backgroundColor: "#27ae60", color: "white" },
                    handler: "onCompare",
                },
            ],
        },

        // Stat comparison table
        {
            xtype: "container",
            reference: "statTable",
            hidden: true,
            margin: "10 0",
            layout: { type: "vbox", align: "center" },
            items: [
                {
                    xtype: "component",
                    reference: "statTableHtml",
                    width: "100%",
                },
            ],
        },

        // Player detail panels
        {
            xtype: "container",
            reference: "detailsContainer",
            layout: { type: "hbox", pack: "center" },
            responsiveConfig: {
                "width < 700": { layout: { type: "vbox", align: "stretch" } },
                "width >= 700": { layout: { type: "hbox", pack: "center" } },
            },
            defaults: {
                xtype: "dls-playerdetails",
                margin: 8,
                flex: 1,
                minWidth: 260,
                maxWidth: 420,
            },
            items: [
                { reference: "player1DetailsCmp" },
                { reference: "player2DetailsCmp" },
                { reference: "player3DetailsCmp", hidden: true },
                { reference: "player4DetailsCmp", hidden: true },
            ],
        },

        // Radar chart
        {
            xtype: "radarchart",
            reference: "radarChartCmp",
            width: 420,
            height: 420,
            margin: 10,
            style: {
                backgroundColor: "rgba(255,255,255,0.85)",
                borderRadius: "8px",
                boxShadow: "0 0 10px rgba(0,0,0,0.1)",
            },
        },
    ],
});