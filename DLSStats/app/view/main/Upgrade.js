Ext.define("DLSStats.view.main.Upgrade", {
    extend: "Ext.container.Container",
    xtype: "dls-upgrade",
    scrollable: true,

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    },

    requires: ["DLSStats.view.main.UpgradeController"],
    controller: "upgrade",
    referenceHolder: true,

    layout: { type: "hbox", align: "stretch" },
    padding: 16,
    responsiveConfig: {
        "width < 700": {
            layout: { type: "vbox", align: "stretch" },
        },
        "width >= 700": {
            layout: { type: "hbox", align: "stretch" },
        },
    },

    items: [
        // ── LEFT: Favorites list ──────────────────────────────
        {
            xtype: "panel",
            title: "Favorites",
            responsiveConfig: {
                "width < 700": { width: null, height: 200, margin: "0 0 12 0" },
                "width >= 700": { width: 260, height: null, margin: "0 12 0 0" },
            },
            width: 260,
            margin: "0 12 0 0",
            layout: "fit",
            style: {
                background: "rgba(255,255,255,0.88)",
                borderRadius: "8px",
                boxShadow: "0 2px 12px rgba(0,0,0,0.2)",
            },
            items: [{
                xtype: "grid",
                reference: "favGrid",
                columnLines: true,
                rowLines: true,
                store: {
                    fields: ["fname", "lname", "pos", "rate", "version", "id",
                             "nat", "club", "foot", "hgt", "spe", "acc", "sta",
                             "str", "con", "pas", "sho", "tac", "prc", "type"],
                    data: [],
                },
                columns: [
                    {
                        text: "Name", flex: 2,
                        renderer: function (v, m, rec) {
                            m.style = "font-weight:bold";
                            return rec.get("fname") + " " + rec.get("lname");
                        },
                    },
                    {
                        text: "Pos", dataIndex: "pos", width: 48, align: "center",
                        renderer: function (value, meta) {
                            var pos = (value || "").toLowerCase();
                            var bg = "black";
                            if (["cf","ss","lw","rw"].indexOf(pos) >= 0) bg = "red";
                            else if (["cm","am","dm","lm","rm","lwb","rwb"].indexOf(pos) >= 0) bg = "yellow";
                            else if (["cb","lb","rb"].indexOf(pos) >= 0) bg = "lime";
                            else if (pos === "gk") bg = "cyan";
                            meta.style = "background:" + bg + ";color:black;font-weight:bold;text-align:center";
                            return value ? value.toUpperCase() : "";
                        },
                    },
                    { text: "OVR", dataIndex: "rate", width: 48, align: "center" },
                ],
                listeners: { itemclick: "onFavSelect" },
            }],
        },

        // ── RIGHT: outer flex container (transparent) ─────────
        {
            xtype: "container",
            flex: 1,
            layout: { type: "vbox", align: "center", pack: "start" },
            items: [
                // White card
                {
                    xtype: "container",
                    layout: { type: "vbox", align: "center" },
                    style: {
                        background: "rgba(255,255,255,0.88)",
                        borderRadius: "8px",
                        boxShadow: "0 2px 12px rgba(0,0,0,0.2)",
                        padding: "16px 20px",
                    },
                    items: [
                        // 1. Disclaimer
                        {
                            xtype: "component",
                            margin: "0 0 12 0",
                            html: "<div style='background:#fff3cd;border:1px solid #ffc107;border-radius:6px;" +
                                  "padding:8px 14px;font-size:12px;color:#856404;max-width:520px;text-align:center'>" +
                                  "⚠️ <b>Simulation only.</b> Results are approximate — actual in-game stats may differ by ±1–2 points per attribute." +
                                  "</div>",
                        },

                        // 2. Mode selector
                        {
                            xtype: "container",
                            layout: { type: "hbox", align: "middle", pack: "center" },
                            margin: "0 0 12 0",
                            items: [
                                {
                                    xtype: "component",
                                    html: "<span style='font-size:12px;font-weight:bold;color:#555;margin-right:8px'>Mode:</span>",
                                },
                                {
                                    xtype: "segmentedbutton",
                                    reference: "modeBtn",
                                    allowMultiple: false,
                                    items: [
                                        { text: "Custom", pressed: true },
                                        { text: "Normal" },
                                    ],
                                    listeners: {
                                        toggle: "onModeChange",
                                    },
                                },
                            ],
                        },

                        // 3. Search row
                        {
                            xtype: "container",
                            layout: { type: "hbox", align: "middle", pack: "center" },
                            margin: "0 0 14 0",
                            defaults: { margin: "0 5" },
                            items: [
                                {
                                    xtype: "textfield",
                                    reference: "idInput",
                                    emptyText: "Player ID (e.g. 8335)",
                                    width: 160,
                                    maskRe: /[0-9]/,
                                    maxLength: 4,
                                    enableKeyEvents: true,
                                    listeners: {
                                        specialkey: function (f, e) {
                                            if (e.getKey() === e.ENTER) {
                                                Ext.ComponentQuery.query("dls-upgrade")[0].getController().onSearch();
                                            }
                                        },
                                    },
                                },
                                {
                                    xtype: "combo",
                                    reference: "versionFilter",
                                    store: { type: "versionstore" },
                                    displayField: "version",
                                    valueField: "version",
                                    queryMode: "local",
                                    editable: false,
                                    value: "20263",
                                    width: 110,
                                },
                                {
                                    xtype: "button",
                                    text: "Load",
                                    style: { backgroundColor: "#2980b9", color: "white" },
                                    handler: "onSearch",
                                },
                            ],
                        },

                        // 4. Upgrade panel (hidden until player loaded)
                        {
                            xtype: "container",
                            reference: "upgradePanel",
                            hidden: true,
                            maxHeight: 520,
                            scrollable: "vertical",
                            layout: { type: "vbox", align: "center" },
                            items: [
                                // OVR circle + info row
                                {
                                    xtype: "container",
                                    layout: { type: "hbox", align: "middle", pack: "center" },
                                    margin: "0 0 16 0",
                                    defaults: { margin: "0 16" },
                                    items: [
                                        {
                                            xtype: "component",
                                            reference: "ovrCircle",
                                            html: '<canvas id="upgrade-ovr-canvas" width="140" height="140"></canvas>',
                                        },
                                        {
                                            xtype: "container",
                                            layout: { type: "vbox", align: "start" },
                                            items: [
                                                {
                                                    xtype: "component",
                                                    reference: "playerNameLabel",
                                                    html: "",
                                                    style: { fontWeight: "bold", fontSize: "17px", color: "#222" },
                                                },
                                                {
                                                    xtype: "component",
                                                    reference: "playerInfoLabel",
                                                    html: "",
                                                    margin: "4 0 0 0",
                                                    style: { fontSize: "12px", color: "#555" },
                                                },
                                                {
                                                    xtype: "component",
                                                    reference: "pointsLabel",
                                                    html: "",
                                                    margin: "8 0 0 0",
                                                    style: { fontSize: "13px" },
                                                },
                                                {
                                                    xtype: "button",
                                                    text: "Reset",
                                                    iconCls: "x-fa fa-undo",
                                                    margin: "10 0 0 0",
                                                    style: { backgroundColor: "#c0392b", color: "white" },
                                                    handler: "onReset",
                                                },
                                            ],
                                        },
                                    ],
                                },

                                // customPanel: statsGrid với arrows
                                {
                                    xtype: "container",
                                    reference: "customPanel",
                                    layout: { type: "vbox", align: "center" },
                                    items: [
                                        {
                                            xtype: "container",
                                            reference: "statsGrid",
                                            layout: { type: "vbox", align: "center" },
                                            items: [
                                                {
                                                    xtype: "container",
                                                    itemId: "statsRow1",
                                                    layout: { type: "hbox", align: "top", pack: "center" },
                                                    margin: "0 0 10 0",
                                                    defaults: { margin: "0 8" },
                                                    items: [],
                                                },
                                                {
                                                    xtype: "container",
                                                    itemId: "statsRow2",
                                                    layout: { type: "hbox", align: "top", pack: "center" },
                                                    defaults: { margin: "0 8" },
                                                    items: [],
                                                },
                                            ],
                                        },
                                    ],
                                },

                                // normalPanel: coach controls + normalStatsGrid
                                {
                                    xtype: "container",
                                    reference: "normalPanel",
                                    hidden: true,
                                    layout: { type: "vbox", align: "center" },
                                    items: [
                                        // Coach type selector
                                        {
                                            xtype: "container",
                                            layout: { type: "hbox", align: "middle", pack: "center" },
                                            margin: "0 0 6 0",
                                            defaults: { margin: "0 5" },
                                            style: { flexWrap: "wrap", rowGap: "4px" },
                                            items: [
                                                {
                                                    xtype: "component",
                                                    html: "<span style='font-size:12px;font-weight:bold;color:#333'>Coach Type:</span>",
                                                    margin: "0 8 0 0",
                                                },
                                                {
                                                    xtype: "button",
                                                    reference: "btnTechnical",
                                                    text: "🎯 Technical",
                                                    enableToggle: true,
                                                    pressed: true,
                                                    toggleGroup: "coachType",
                                                    style: { minWidth: "110px" },
                                                    listeners: { toggle: "onCoachTypeToggle" },
                                                },
                                                {
                                                    xtype: "button",
                                                    reference: "btnFitness",
                                                    text: "💪 Fitness",
                                                    enableToggle: true,
                                                    pressed: false,
                                                    toggleGroup: "coachType",
                                                    style: { minWidth: "110px" },
                                                    listeners: { toggle: "onCoachTypeToggle" },
                                                },
                                                {
                                                    xtype: "button",
                                                    reference: "btnGoalkeeping",
                                                    text: "🧤 Goalkeeping",
                                                    enableToggle: true,
                                                    pressed: false,
                                                    hidden: true,
                                                    toggleGroup: "coachType",
                                                    style: { minWidth: "120px", backgroundColor: "#16a085", color: "white" },
                                                    listeners: { toggle: "onCoachTypeToggle" },
                                                },
                                            ],
                                        },
                                        // Coach tier selector
                                        {
                                            xtype: "container",
                                            layout: { type: "hbox", align: "middle", pack: "center" },
                                            margin: "0 0 6 0",
                                            defaults: { margin: "0 5" },
                                            style: { flexWrap: "wrap", rowGap: "4px" },
                                            items: [
                                                {
                                                    xtype: "component",
                                                    html: "<span style='font-size:12px;font-weight:bold;color:#333'>Coach Tier:</span>",
                                                    margin: "0 8 0 0",
                                                },
                                                {
                                                    xtype: "button",
                                                    reference: "btnCommon",
                                                    text: "Common",
                                                    enableToggle: true,
                                                    pressed: true,
                                                    toggleGroup: "coachTier",
                                                    style: { minWidth: "90px", backgroundColor: "#7f8c8d", color: "white" },
                                                    listeners: { toggle: "onCoachTierToggle" },
                                                },
                                                {
                                                    xtype: "button",
                                                    reference: "btnRare",
                                                    text: "Rare",
                                                    enableToggle: true,
                                                    pressed: false,
                                                    toggleGroup: "coachTier",
                                                    style: { minWidth: "90px", backgroundColor: "#2980b9", color: "white" },
                                                    listeners: { toggle: "onCoachTierToggle" },
                                                },
                                                {
                                                    xtype: "button",
                                                    reference: "btnLegendary",
                                                    text: "⭐ Legendary",
                                                    enableToggle: true,
                                                    pressed: false,
                                                    toggleGroup: "coachTier",
                                                    style: { minWidth: "110px", backgroundColor: "#f39c12", color: "white" },
                                                    listeners: { toggle: "onCoachTierToggle" },
                                                },
                                            ],
                                        },
                                        // Coach info label
                                        {
                                            xtype: "component",
                                            reference: "coachInfoLabel",
                                            margin: "0 0 10 0",
                                            html: "<div style='font-size:11px;color:#555;text-align:center'>" +
                                                  "Common: +1 to 1 stat &nbsp;|&nbsp; 5% breakthrough (+1 extra)" +
                                                  "</div>",
                                        },
                                        // Train button
                                        {
                                            xtype: "button",
                                            text: "▶ Train",
                                            margin: "0 0 8 0",
                                            style: { backgroundColor: "#8e44ad", color: "white", fontWeight: "bold" },
                                            handler: "onApplyCoach",
                                        },
                                        // normalStatsGrid: 2 rows × 4 cols, no arrows
                                        {
                                            xtype: "container",
                                            reference: "normalStatsGrid",
                                            layout: { type: "vbox", align: "center" },
                                            items: [
                                                {
                                                    xtype: "container",
                                                    itemId: "normalStatsRow1",
                                                    layout: { type: "hbox", align: "top", pack: "center" },
                                                    margin: "0 0 10 0",
                                                    defaults: { margin: "0 8" },
                                                    items: [],
                                                },
                                                {
                                                    xtype: "container",
                                                    itemId: "normalStatsRow2",
                                                    layout: { type: "hbox", align: "top", pack: "center" },
                                                    defaults: { margin: "0 8" },
                                                    items: [],
                                                },
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    ],
});
