Ext.define("DLSStats.view.main.UpgradeController", {
    extend: "Ext.app.ViewController",
    alias: "controller.upgrade",

    _player: null,
    _current: null,
    _maxPoints: 0,

    // Stat order: row1 = SPE ACC STA STR, row2 = CON PAS SHO TAC
    STATS: ["spe", "acc", "sta", "str", "con", "pas", "sho", "tac"],
    STAT_LABELS: {
        spe: "SPE", acc: "ACC", sta: "STA", str: "STR",
        con: "CON", pas: "PAS", sho: "SHO", tac: "TAC"
    },

    // Trọng số điểm: 1 điểm nâng cấp = weight điểm thực
    // CON = 2x, STR = 1.5x, còn lại = 1x
    STAT_WEIGHTS: {
        spe: 1, acc: 1, sta: 1, str: 1.5,
        con: 2, pas: 1, sho: 1, tac: 1
    },

    init: function () {
        this._loadFavorites();
    },

    _loadFavorites: function () {
        var me = this;
        var grid = me.lookupReference("favGrid");
        if (!grid) return;
        try {
            var list = JSON.parse(localStorage.getItem("dls_favorites") || "[]");
            grid.getStore().loadData(list);
        } catch (e) {}
    },

    // Deterministic max points: 87-92 based on id
    _calcMaxPoints: function (id) {
        return 87 + (parseInt(id, 10) % 6);
    },

    onFavSelect: function (grid, record) {
        this._loadPlayer(record.data);
    },

    onSearch: function () {
        var me = this;
        var id  = me.lookupReference("idInput").getValue().trim();
        var ver = me.lookupReference("versionFilter").getValue();
        if (!id) return;

        var playerStore = Ext.getStore("playerstore");
        if (!playerStore || !playerStore.isLoaded()) {
            Ext.Msg.alert("Error", "Player store not loaded yet.");
            return;
        }

        var results = playerStore.queryBy(function (rec) {
            return String(rec.get("id")) === String(id) &&
                   String(rec.get("version")) === String(ver);
        }).getRange();

        if (results.length === 0) {
            Ext.Msg.alert("Not Found", "No player found with ID " + id + " in version " + ver);
            return;
        }
        me._loadPlayer(results[0].data);
    },

    _loadPlayer: function (playerData) {
        var me = this;
        me._player    = Ext.clone(playerData);
        me._current   = Ext.clone(playerData);
        me._maxPoints = me._calcMaxPoints(me._player.id);
        me._usedExtra = 0;

        me._buildStatCells();

        // upgradePanel phải visible trước khi canvas có trong DOM
        var panel = me.lookupReference("upgradePanel");
        panel.setVisible(true);

        // Đợi DOM render xong rồi mới vẽ canvas
        Ext.defer(function () {
            me._updateDisplay();
        }, 50);
    },

    onReset: function () {
        var me = this;
        if (!me._player) return;
        me._current   = Ext.clone(me._player);
        me._usedExtra = 0;
        me._syncStatCells();
        me._updateDisplay();
    },

    // ── Build stat cells ──────────────────────────────────────
    _buildStatCells: function () {
        var me = this;
        var statsGrid = me.lookupReference("statsGrid");
        var row1 = statsGrid.down("#statsRow1");
        var row2 = statsGrid.down("#statsRow2");
        row1.removeAll(true);
        row2.removeAll(true);

        var row1Stats = ["spe", "acc", "sta", "str"];
        var row2Stats = ["con", "pas", "sho", "tac"];

        row1Stats.forEach(function (stat) { row1.add(me._makeStatCell(stat)); });
        row2Stats.forEach(function (stat) { row2.add(me._makeStatCell(stat)); });
    },

    _makeStatCell: function (stat) {
        var me = this;
        var label  = me.STAT_LABELS[stat];
        var weight = me.STAT_WEIGHTS[stat];
        var weightBadge = weight !== 1
            ? "<span style='font-size:9px;color:#f1c40f;margin-left:2px'>×" + weight + "</span>"
            : "";

        return {
            xtype: "container",
            itemId: "cell_" + stat,
            layout: { type: "vbox", align: "center" },
            width: 80,
            items: [
                // Stat name + weight badge
                {
                    xtype: "component",
                    html: "<span style='font-size:11px;font-weight:bold;color:#2471a3'>" +
                          label + "</span>" + weightBadge,
                    margin: "0 0 4 0",
                    style: { textAlign: "center" },
                },
                // Circle + arrows row
                {
                    xtype: "container",
                    layout: { type: "hbox", align: "middle", pack: "center" },
                    items: [
                        // Value circle (canvas)
                        {
                            xtype: "component",
                            itemId: "canvas_" + stat,
                            html: '<canvas id="stat-canvas-' + stat + '" width="56" height="56"></canvas>',
                        },
                        // Up/Down arrows stacked
                        {
                            xtype: "container",
                            layout: { type: "vbox", align: "center" },
                            margin: "0 0 0 4",
                            items: [
                                {
                                    xtype: "button",
                                    iconCls: "x-fa fa-caret-up",
                                    width: 24, height: 22,
                                    style: { backgroundColor: "#27ae60", color: "white",
                                             padding: "0", minWidth: "0" },
                                    margin: "0 0 2 0",
                                    handler: function () { me._adjustStat(stat, +1); },
                                },
                                {
                                    xtype: "button",
                                    iconCls: "x-fa fa-caret-down",
                                    width: 24, height: 22,
                                    style: { backgroundColor: "#c0392b", color: "white",
                                             padding: "0", minWidth: "0" },
                                    handler: function () { me._adjustStat(stat, -1); },
                                },
                            ],
                        },
                    ],
                },
                // Delta badge
                {
                    xtype: "component",
                    itemId: "delta_" + stat,
                    html: "&nbsp;",
                    margin: "3 0 0 0",
                    style: { textAlign: "center", minHeight: "16px" },
                },
            ],
        };
    },

    // ── Adjust stat ───────────────────────────────────────────
    _adjustStat: function (stat, delta) {
        var me = this;
        if (!me._player) return;

        var base    = me._player[stat]   || 0;
        var current = me._current[stat]  || 0;
        var newVal  = current + delta;

        if (newVal < base) return;
        if (newVal > 100)  return;

        var weight       = me.STAT_WEIGHTS[stat];
        var usedWeighted = me._calcUsedWeighted();
        var remaining    = me._maxPoints - usedWeighted;

        if (delta > 0) {
            if (remaining <= 0) return; // đã max, không làm gì

            if (weight <= remaining) {
                // Đủ điểm → tăng stat bình thường
                me._current[stat] = newVal;
            } else {
                // Không đủ điểm cho 1 bậc đầy đủ →
                // tiêu hết điểm còn lại để đạt max budget,
                // nhưng stat KHÔNG tăng (chỉ số giữ nguyên)
                // Dùng một "phantom" point để đánh dấu budget đã hết
                // bằng cách cộng phần dư vào _usedExtra
                me._usedExtra = (me._usedExtra || 0) + remaining;
            }
        } else {
            // Giảm stat
            me._current[stat] = newVal;
            // Nếu có extra points đã tiêu, hoàn lại khi giảm
            if (me._usedExtra && me._usedExtra > 0) {
                me._usedExtra = 0;
            }
        }

        me._syncStatCells();
        me._updateDisplay();
    },

    // Total weighted points used (bao gồm extra phantom points)
    _calcUsedWeighted: function () {
        var me = this;
        var total = me._usedExtra || 0;
        me.STATS.forEach(function (stat) {
            var diff = (me._current[stat] || 0) - (me._player[stat] || 0);
            total += diff * me.STAT_WEIGHTS[stat];
        });
        return total;
    },

    // ── Sync stat cell canvases ───────────────────────────────
    _syncStatCells: function () {
        var me = this;
        me.STATS.forEach(function (stat) {
            me._drawStatCircle(stat);
            me._updateDelta(stat);
        });
    },

    _drawStatCircle: function (stat) {
        var me = this;
        var val    = me._current[stat] || 0;
        var base   = me._player[stat]  || 0;
        var canvas = document.getElementById("stat-canvas-" + stat);
        if (!canvas) return;

        var ctx = canvas.getContext("2d");
        var W = 56, H = 56, cx = W / 2, cy = H / 2, R = 24;
        ctx.clearRect(0, 0, W, H);

        // Black background circle
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.fillStyle = "#000";
        ctx.fill();

        // Thin border — highlight if upgraded
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.strokeStyle = val > base ? "#2ecc71" : "rgba(255,255,255,0.2)";
        ctx.lineWidth = val > base ? 2.5 : 1.5;
        ctx.stroke();

        // Value text
        ctx.font = "bold 16px Arial";
        ctx.fillStyle = me._statColor(val);
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(String(val), cx, cy);
    },

    _updateDelta: function (stat) {
        var me = this;
        var statsGrid = me.lookupReference("statsGrid");
        if (!statsGrid) return;
        var deltaCmp = statsGrid.down("#delta_" + stat);
        if (!deltaCmp) return;

        var diff = (me._current[stat] || 0) - (me._player[stat] || 0);
        if (diff > 0) {
            deltaCmp.setHtml("<span style='color:#2ecc71;font-weight:bold;font-size:11px'>+" + diff + "</span>");
        } else {
            deltaCmp.setHtml("&nbsp;");
        }
    },

    _statColor: function (val) {
        if (val >= 90) return "cyan";
        if (val >= 80) return "lime";
        if (val >= 70) return "yellow";
        if (val >= 60) return "orange";
        if (val >= 50) return "crimson";
        return "red";
    },

    // ── Update OVR circle + labels ────────────────────────────
    _updateDisplay: function () {
        var me = this;
        var used    = me._calcUsedWeighted();
        var max     = me._maxPoints;
        var baseOvr = me._player.rate || 0;
        var isMax   = used >= max;

        // OVR tăng dần: baseOvr + (used/max) * 10, tối đa baseOvr + 10
        var ovrBonus = max > 0 ? Math.min((used / max) * 10, 10) : 0;
        var dispOvr  = (baseOvr + ovrBonus).toFixed(1);
        // Nếu là số nguyên thì bỏ .0
        if (dispOvr.endsWith(".0")) dispOvr = String(baseOvr + Math.round(ovrBonus));

        // Name
        var nameLabel = me.lookupReference("playerNameLabel");
        if (nameLabel) {
            nameLabel.setHtml(me._player.fname + " " + me._player.lname);
        }

        // Info
        var infoLabel = me.lookupReference("playerInfoLabel");
        if (infoLabel) {
            infoLabel.setHtml(
                me._player.pos + " &nbsp;|&nbsp; " + me._player.nat +
                " &nbsp;|&nbsp; " + (me._player.club || "") +
                " &nbsp;|&nbsp; v" + me._player.version
            );
        }

        // Points
        var pointsLabel = me.lookupReference("pointsLabel");
        if (pointsLabel) {
            pointsLabel.setHtml(
                "<span style='color:#e67e22;font-weight:bold'>" +
                used.toFixed(1) + " / " + max + "</span>" +
                " <span style='color:#555'>pts used</span>" +
                (isMax ? " &nbsp;<span style='color:#27ae60;font-weight:bold'>MAX ✓</span>" : "")
            );
        }

        me._drawOvrCircle(dispOvr, baseOvr, used, max);
        me._syncStatCells();
    },

    _drawOvrCircle: function (dispOvr, baseOvr, used, max) {
        var canvas = document.getElementById("upgrade-ovr-canvas");
        if (!canvas) return;
        var ctx = canvas.getContext("2d");
        var W = 140, H = 140, cx = W / 2, cy = H / 2, R = 58;

        ctx.clearRect(0, 0, W, H);

        // Màu nền theo ngưỡng OVR (giống màu stat phụ)
        var ovrNum = parseFloat(dispOvr) || baseOvr;
        var bgColor;
        if (ovrNum >= 90)      bgColor = "cyan";
        else if (ovrNum >= 80) bgColor = "lime";
        else if (ovrNum >= 70) bgColor = "yellow";
        else if (ovrNum >= 60) bgColor = "orange";
        else if (ovrNum >= 50) bgColor = "crimson";
        else                   bgColor = "red";

        // Filled background circle
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.fillStyle = bgColor;
        ctx.fill();

        // Track ring — đen full
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 9;
        ctx.stroke();

        // Progress arc from 12 o'clock — teal
        var progress = max > 0 ? Math.min(used / max, 1) : 0;
        if (progress > 0) {
            var startAngle = -Math.PI / 2;
            var endAngle   = startAngle + progress * Math.PI * 2;
            ctx.beginPath();
            ctx.arc(cx, cy, R, startAngle, endAngle);
            ctx.strokeStyle = "#1abc9c";
            ctx.lineWidth = 9;
            ctx.lineCap = "round";
            ctx.stroke();
        }

        // OVR number — chữ trắng
        var isMax = used >= max;
        var fontSize = String(dispOvr).indexOf(".") !== -1 ? "bold 26px Arial" : "bold 34px Arial";
        ctx.font = fontSize;
        ctx.fillStyle = "#fff";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(String(dispOvr), cx, cy - 8);

        // "OVR" sub-label
        ctx.font = "11px Arial";
        ctx.fillStyle = "rgba(255,255,255,0.85)";
        ctx.fillText("OVR", cx, cy + 14);

        // Base OVR hint when maxed
        if (isMax) {
            ctx.font = "10px Arial";
            ctx.fillStyle = "rgba(255,255,255,0.65)";
            ctx.fillText("base " + baseOvr, cx, cy + 28);
        }
    },
});
