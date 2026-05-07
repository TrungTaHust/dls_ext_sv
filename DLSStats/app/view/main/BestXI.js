Ext.define("DLSStats.view.main.BestXI", {
    extend: "Ext.container.Container",
    xtype: "dls-bestxi",
    scrollable: true,

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    },

    requires: ["DLSStats.view.main.BestXIController"],
    controller: "bestxi",
    referenceHolder: true,

    layout: { type: "vbox", align: "center" },
    padding: 10,

    items: [
        // Toolbar: Formation + Buttons + Rating badge
        {
            xtype: "container",
            layout: { type: "hbox", align: "middle", pack: "center" },
            margin: "0 0 10 0",
            defaults: { margin: "0 4" },
            style: { flexWrap: "wrap", rowGap: "6px" },
            items: [
                { xtype: "component", html: "<b style='color:#fff;text-shadow:0 1px 3px rgba(0,0,0,0.8)'>Formation:</b>" },
                {
                    xtype: "combo",
                    reference: "formationCombo",
                    width: 110,
                    queryMode: "local",
                    editable: false,
                    store: [
                        "4-5-1", "4-2-3-1", "4-1-4-1", "4-3-2-1",
                        "4-4-2", "4-3-1-2", "4-1-2-1-2", "4-1-3-2", "4-2-2-2", "4-4-1-1",
                        "4-3-3", "4-1-2-3", "4-2-1-3",
                        "5-3-2", "5-2-1-2",
                        "5-2-3", "5-2-2-1",
                        "5-4-1", "5-1-2-1-1",
                        "3-5-2", "3-2-3-2", "3-4-1-2", "3-1-4-2", "3-5-1-1",
                        "3-4-3", "3-4-2-1", "3-3-1-3", "3-1-2-1-3",
                    ],
                    value: "4-3-3",
                    listeners: { select: "onFormationChange" },
                },
                {
                    xtype: "button",
                    text: "Auto Pick",
                    iconCls: "x-fa fa-magic",
                    style: { backgroundColor: "#2980b9", color: "white" },
                    handler: "onAutoPick",
                },
                {
                    xtype: "button",
                    text: "Clear XI",
                    iconCls: "x-fa fa-times",
                    style: { backgroundColor: "#c0392b", color: "white" },
                    handler: "onClearXI",
                },
                // Rating badge
                {
                    xtype: "component",
                    reference: "totalRating",
                    margin: "0 0 0 4",
                    html: "<div style='" +
                        "background:rgba(0,0,0,0.65);" +
                        "border:2px solid rgba(255,255,255,0.3);" +
                        "border-radius:8px;" +
                        "padding:6px 12px;" +
                        "color:#fff;" +
                        "font-size:13px;" +
                        "font-weight:bold;" +
                        "text-shadow:0 1px 2px rgba(0,0,0,0.8);" +
                        "white-space:nowrap;" +
                        "'>Team Rating: <span style='color:#f1c40f;font-size:18px'>-</span></div>",
                },
            ],
        },

        // Pitch — responsive: chiều rộng 100% viewport, tỉ lệ cố định 500:680
        {
            xtype: "component",
            reference: "pitch",
            style: {
                background: "linear-gradient(180deg,#2d8a4e 0%,#3aad63 50%,#2d8a4e 100%)",
                border: "3px solid #fff",
                borderRadius: "8px",
                position: "relative",
                overflow: "hidden",
                width: "min(500px, 96vw)",
                height: "calc(min(500px, 96vw) * 1.36)",
            },
            html: '<div id="dls-pitch-inner" style="position:relative;width:100%;height:100%"></div>',
        },
    ],
});


