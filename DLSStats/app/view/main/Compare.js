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

    requires: ["DLSStats.view.main.PlayerController"],

    controller: "player",
    referenceHolder: true,

    layout: {
        type: "vbox",
        align: "center",
        pack: "center",
    },

    items: [
        // ID & version inputs
        {
            xtype: "container",
            reference: "inputContainer",
            layout: {
                type: "hbox",
                pack: "center",
                align: "middle",
            },
            defaults: {
                xtype: "textfield",
                margin: 10,
                flex: 1,
                minWidth: 120,
            },
            items: [
                {
                    itemId: "player1Id",
                    emptyText: "Enter player1's ID",
                },
                {
                    xtype: "combo",
                    itemId: "version1",
                    name: "version1",
                    emptyText: "Version of ID1",
                    store: ["20253", "20252", "20251", "20242", "20241", "20231"],
                    queryMode: "local",
                    editable: false,
                    margin: 10,
                    flex: 1,
                    minWidth: 120,
                },
                {
                    itemId: "player2Id",
                    emptyText: "Enter player2's ID",
                },
                {
                    xtype: "combo",
                    itemId: "version2",
                    name: "version2",
                    emptyText: "Version of ID2",
                    store: ["20253", "20252", "20251", "20242", "20241", "20231"],
                    queryMode: "local",
                    editable: false,
                    margin: 10,
                    flex: 1,
                    minWidth: 120,
                },
            ],
        },
        // Button Compare
        {
            xtype: "button",
            text: "Compare",
            width: 120,
            style: {
                backgroundColor: "green",
                color: "black",
            },
            margin: 10,
            handler: function (btn) {
                var mainContainer = btn.up("dls-compare");
                var ctrl = mainContainer.getController();

                var inputContainer = mainContainer.lookupReference("inputContainer");

                var player1Id = inputContainer.down("#player1Id").getValue();
                var version1 = inputContainer.down("#version1").getValue();
                var player2Id = inputContainer.down("#player2Id").getValue();
                var version2 = inputContainer.down("#version2").getValue();

                // Chuẩn bị criteria cho tìm kiếm
                var criteria1 = {
                    id: String(player1Id),
                    version: String(version1)
                };
                var criteria2 = {
                    id: String(player2Id),
                    version: String(version2)
                };

                // Tìm trong store local qua hàm dùng chung
                var player1Results = ctrl.searchPlayersByCriteria(criteria1, null);
                var player2Results = ctrl.searchPlayersByCriteria(criteria2, null);

                var player1 = player1Results.length > 0 ? player1Results[0].data : null;
                var player2 = player2Results.length > 0 ? player2Results[0].data : null;

                if (!player1 || !player2) {
                    Ext.Msg.alert(
                        "Not Found",
                        "One or both player data of corresponding version not found."
                    );
                    return;
                }

                var player1DetailsCmp = mainContainer.lookupReference("player1DetailsCmp");
                var player2DetailsCmp = mainContainer.lookupReference("player2DetailsCmp");
                player1DetailsCmp.updatePlayer(player1);
                player2DetailsCmp.updatePlayer(player2);

                var radarChartCmp = mainContainer.lookupReference("radarChartCmp");
                radarChartCmp.updatePlayers([player1, player2]);
            },
        },
        // 2 players detail panels
        {
            xtype: "container",
            reference: "detailsContainer",
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
                xtype: "panel",
                margin: 10,
                scrollable: true,
                style: {
                    border: "1px solid #ccc",
                    backgroundColor: "#fafafa",
                },
                flex: 1,
                minWidth: 280,
                maxWidth: 500,
            },
            items: [
                {
                    itemId: "player1Details",
                    xtype: "dls-playerdetails",
                    reference: "player1DetailsCmp",
                },
                {
                    itemId: "player2Details",
                    xtype: "dls-playerdetails",
                    reference: "player2DetailsCmp",
                },
            ],
        },
        // Radar chart container
        {
            xtype: "radarchart",
            reference: "radarChartCmp",
            width: 400,
            height: 400,
            margin: 10,
            style: {
                backgroundColor: "rgba(255, 255, 255, 0.8)",
                borderRadius: "8px",
                boxShadow: "0 0 10px rgba(0,0,0,0.1)",
            },
            hidden: false,
        },
    ],
});
