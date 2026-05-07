Ext.define("DLSStats.view.main.TeamShowcase", {
    extend: "Ext.container.Container",
    xtype: "dls-teamshowcase",
    scrollable: true,

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    },

    requires: ["DLSStats.view.main.TeamShowcaseController"],
    controller: "teamshowcase",
    referenceHolder: true,

    layout: { type: "vbox", align: "center" },
    padding: 10,

    items: [
        // Selector row
        {
            xtype: "container",
            layout: { type: "hbox", align: "middle", pack: "center" },
            margin: "0 0 10 0",
            defaults: { margin: "0 6" },
            style: { flexWrap: "wrap", rowGap: "6px" },
            items: [
                {
                    xtype: "segmentedbutton",
                    reference: "modeBtn",
                    items: [
                        { text: "Nation", pressed: true },
                        { text: "Club" },
                    ],
                    listeners: { toggle: "onModeToggle" },
                },
                {
                    xtype: "combo",
                    reference: "nationCombo",
                    emptyText: "Select Nation...",
                    store: { fields: ["name"], data: [] },
                    displayField: "name",
                    valueField: "name",
                    queryMode: "local",
                    typeAhead: false,
                    anyMatch: true,
                    forceSelection: true,
                    width: 170,
                    listeners: { select: "onCriteriaSelect" },
                },
                {
                    xtype: "combo",
                    reference: "clubCombo",
                    emptyText: "Select Club...",
                    store: { fields: ["name"], data: [] },
                    displayField: "name",
                    valueField: "name",
                    queryMode: "local",
                    typeAhead: false,
                    anyMatch: true,
                    forceSelection: true,
                    width: 170,
                    hidden: true,
                    listeners: { select: "onCriteriaSelect" },
                },
                {
                    xtype: "component",
                    reference: "infoLabel",
                    html: "",
                    style: {
                        background: "rgba(0,0,0,0.65)",
                        borderRadius: "6px",
                        padding: "4px 10px",
                        color: "#fff",
                        fontSize: "13px",
                    },
                },
            ],
        },

        // Main content: pitch + bench + player detail
        // Trên mobile: vbox (dọc), trên desktop: hbox (ngang)
        {
            xtype: "container",
            layout: { type: "hbox", align: "top" },
            responsiveConfig: {
                "width < 700": { layout: { type: "vbox", align: "center" } },
                "width >= 700": { layout: { type: "hbox", align: "top" } },
            },
            defaults: { margin: "0 6 8 6" },
            items: [
                // Pitch — responsive width
                {
                    xtype: "component",
                    reference: "showcasePitch",
                    style: {
                        background: "linear-gradient(180deg,#2d8a4e 0%,#3aad63 50%,#2d8a4e 100%)",
                        border: "3px solid #fff",
                        borderRadius: "8px",
                        position: "relative",
                        overflow: "hidden",
                        width: "min(500px, 96vw)",
                        height: "calc(min(500px, 96vw) * 1.36)",
                    },
                    html: '<div id="dls-showcase-pitch-inner" style="position:relative;width:100%;height:100%"></div>',
                },

                // Bench panel — responsive width
                {
                    xtype: "component",
                    reference: "benchPanel",
                    style: {
                        background: "rgba(15,15,15,0.92)",
                        border: "3px solid rgba(255,255,255,0.6)",
                        borderRadius: "8px",
                        overflow: "hidden",
                        width: "min(200px, 96vw)",
                        minHeight: "200px",
                    },
                    html: '<div id="dls-showcase-bench" style="width:100%;height:100%;padding:8px;box-sizing:border-box">' +
                        '<div style="color:#fff;font-weight:bold;text-align:center;font-size:13px;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.4);padding-bottom:6px">SUBSTITUTES</div>' +
                        '</div>',
                },

                // Player detail panel
                {
                    xtype: "dls-playerdetails",
                    reference: "showcasePlayerDetails",
                    width: 300,
                    responsiveConfig: {
                        "width < 700": { width: null, style: { width: "min(300px, 96vw)" } },
                        "width >= 700": { width: 300 },
                    },
                },
            ],
        },
    ],
});