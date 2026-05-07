Ext.define("DLSStats.view.main.Favorites", {
    extend: "Ext.container.Container",
    xtype: "dls-favorites",

    layout: { type: "vbox", align: "center", pack: "start" },
    padding: 10,
    scrollable: true,

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    },

    requires: ["DLSStats.view.main.FavoritesController", "DLSStats.view.main.PlayerDetails"],

    controller: "favorites",
    referenceHolder: true,

    items: [
        // Favorites grid + player detail side by side, căn giữa
        {
            xtype: "container",
            layout: { type: "hbox", align: "top", pack: "center" },
            responsiveConfig: {
                "width < 700": { layout: { type: "vbox", align: "center" } },
                "width >= 700": { layout: { type: "hbox", align: "top", pack: "center" } },
            },
            defaults: { margin: 10 },
            items: [
                // Favorites panel
                {
                    xtype: "panel",
                    title: "Favorites",
                    responsiveConfig: {
                        "width < 700": { width: null, style: { width: "min(380px, 96vw)" } },
                        "width >= 700": { width: 380 },
                    },
                    width: 380,
                    tbar: [
                        "->",
                        {
                            xtype: "button",
                            text: "Clear All",
                            iconCls: "x-fa fa-trash",
                            handler: "onClearAll",
                        },
                    ],
                    items: [
                        {
                            xtype: "grid",
                            reference: "favoritesGrid",
                            columnLines: true,
                            rowLines: true,
                            disableSelection: false,
                            store: {
                                fields: ["fname", "lname", "pos", "rate", "version", "id", "nat", "club",
                                    "foot", "hgt", "spe", "acc", "sta", "str", "con", "pas", "sho", "tac", "prc", "type"],
                                data: [],
                            },
                            columns: [
                                {
                                    text: "Name", flex: 2, minWidth: 130,
                                    renderer: function (v, m, rec) {
                                        m.style = "font-weight:bold";
                                        return rec.get("fname") + " " + rec.get("lname");
                                    },
                                },
                                {
                                    text: "Pos", dataIndex: "pos", align: "center", width: 55,
                                    renderer: function (value, meta) {
                                        var pos = (value || "").toLowerCase();
                                        var bg = "black";
                                        if (["cf", "ss", "lw", "rw"].indexOf(pos) >= 0) bg = "red";
                                        else if (["cm", "am", "dm", "lm", "rm", "lwb", "rwb"].indexOf(pos) >= 0) bg = "yellow";
                                        else if (["cb", "lb", "rb"].indexOf(pos) >= 0) bg = "lime";
                                        else if (pos === "gk") bg = "cyan";
                                        meta.style = "background-color:" + bg + ";color:black;font-weight:bold;text-align:center";
                                        return value ? value.toUpperCase() : "";
                                    },
                                },
                                { text: "OVR", dataIndex: "rate", align: "center", width: 55 },
                                {
                                    xtype: "actioncolumn", width: 40, align: "center",
                                    items: [{
                                        iconCls: "x-fa fa-star",
                                        tooltip: "Remove",
                                        handler: "onRemoveFavorite",
                                    }],
                                },
                            ],
                            listeners: { itemclick: "onFavoriteSelect" },
                        },
                    ],
                    // Paging toolbar
                    bbar: {
                        xtype: "toolbar",
                        items: [
                            "->",
                            {
                                xtype: "button",
                                text: "Back",
                                reference: "favPrevBtn",
                                disabled: true,
                                style: { backgroundColor: "green" },
                                handler: "onFavPrev",
                                listeners: {
                                    afterrender: function (btn) {
                                        var inner = btn.el.dom.querySelector(".x-btn-inner");
                                        if (inner) inner.style.color = "black";
                                    },
                                },
                            },
                            {
                                xtype: "component",
                                reference: "favPageLabel",
                                html: "<span style='color:#333;font-weight:bold'>-</span>",
                                margin: "0 8",
                            },
                            {
                                xtype: "button",
                                text: "Next",
                                reference: "favNextBtn",
                                disabled: true,
                                style: { backgroundColor: "green" },
                                handler: "onFavNext",
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
                },

                // Player detail — chiều cao tự co theo nội dung
                {
                    xtype: "dls-playerdetails",
                    reference: "playerdetails",
                    responsiveConfig: {
                        "width < 700": { width: null, style: { width: "min(340px, 96vw)" } },
                        "width >= 700": { width: 340 },
                    },
                    width: 340,
                },
            ],
        },
    ],
});
