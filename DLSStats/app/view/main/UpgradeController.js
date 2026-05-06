Ext.define("DLSStats.view.main.UpgradeController", {
    extend: "Ext.app.ViewController",
    alias: "controller.upgrade",

    _player: null,
    _current: null,
    _maxPoints: 0,
    _usedExtra: 0,
    _mode: "custom",

    // Stat order: row1 = SPE ACC STA STR, row2 = CON PAS SHO TAC
    STATS: ["spe", "acc", "sta", "str", "con", "pas", "sho", "tac"],
    STAT_LABELS: {
        spe: "SPE", acc: "ACC", sta: "STA", str: "STR",
        con: "CON", pas: "PAS", sho: "SHO", tac: "TAC"
    },

    // Trọng số điểm mỗi bậc nâng cấp
    STAT_WEIGHTS: {
        spe: 1.0, acc: 1.0, sta: 1.0, str: 1.5,
        con: 2,   pas: 1.0, sho: 1.0, tac: 1.0
    },

    // Coach config
    COACH_TYPES: {
        technical: ["con", "pas", "sho", "tac"],
        fitness:   ["spe", "acc", "sta", "str"]
    },
    COACH_TIERS: {
        common:    { count: 1, bonus: 1, breakChance: 0.05 },
        rare:      { count: 2, bonus: 2, breakChance: 0.10 },
        legendary: { count: 3, bonus: 3, breakChance: 0.20 }
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

    // Deterministic max points: 80-85 based on id
    _calcMaxPoints: function (id) {
        return 80 + (parseInt(id, 10) % 6);
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

        // Giữ nguyên mode hiện tại, KHÔNG reset về custom
        var currentMode = me._mode || "custom";
        var customPanel = me.lookupReference("customPanel");
        var normalPanel = me.lookupReference("normalPanel");

        me._buildStatCells();
        me._buildNormalStatCells();

        // Hiện đúng panel theo mode hiện tại
        if (customPanel) customPanel.setVisible(currentMode === "custom");
        if (normalPanel) normalPanel.setVisible(currentMode === "normal");

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
        me._syncNormalStatCells();
        me._updateDisplay();
    },

    // ── Mode change ───────────────────────────────────────────
    onModeChange: function (container, button, pressed) {
        var me = this;
        if (!pressed) return;
        var text = button.getText();
        var customPanel = me.lookupReference("customPanel");
        var normalPanel = me.lookupReference("normalPanel");
        if (text === "Custom") {
            me._mode = "custom";
            if (customPanel) customPanel.setVisible(true);
            if (normalPanel) normalPanel.setVisible(false);
            if (me._player) {
                Ext.defer(function () { me._syncStatCells(); }, 30);
            }
        } else if (text === "Normal") {
            me._mode = "normal";
            if (customPanel) customPanel.setVisible(false);
            if (normalPanel) normalPanel.setVisible(true);
            // Defer để DOM render normalPanel xong rồi mới vẽ canvas
            if (me._player) {
                Ext.defer(function () { me._syncNormalStatCells(); }, 30);
            }
        }
    },

    // ── Apply Coach (Normal mode) ─────────────────────────────
    onApplyCoach: function () {
        var me = this;
        if (!me._player) return;

        var coachTypeText = me._getSelectedType();   // "technical" or "fitness"
        var coachTierText = me._getSelectedTier();   // "common", "rare", "legendary"

        var typePool = me.COACH_TYPES[coachTypeText];
        var tier     = me.COACH_TIERS[coachTierText];

        if (!typePool || !tier) return;

        // Lọc pool: chỉ lấy stats có _current[stat] < 100
        var pool = typePool.filter(function (stat) {
            return (me._current[stat] || 0) < 100;
        });

        if (pool.length === 0) {
            Ext.Msg.alert("All maxed!", "All stats in this coach's pool are already at 100.");
            return;
        }

        // Chọn ngẫu nhiên tier.count stats từ pool (không trùng)
        var count = Math.min(tier.count, pool.length);
        var shuffled = pool.slice();
        for (var i = shuffled.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var tmp = shuffled[i];
            shuffled[i] = shuffled[j];
            shuffled[j] = tmp;
        }
        var chosen = shuffled.slice(0, count);

        // Roll breakthrough
        var breakthrough = Math.random() < tier.breakChance;
        var bonusPerStat = tier.bonus + (breakthrough ? 1 : 0);

        // Kiểm tra budget còn lại
        var usedBefore = me._calcUsedWeighted();
        var remaining  = me._maxPoints - usedBefore;

        // Áp dụng bonus và tính weighted points
        var changes = [];

        if (remaining <= 0) {
            // Hết budget hoàn toàn
            Ext.toast({ html: "Already at MAX! No points remaining.", align: "b", minWidth: 220 });
            return;
        }

        // Tính tổng weighted cost nếu train đầy đủ
        var totalWeightedCost = 0;
        chosen.forEach(function (stat) {
            totalWeightedCost += bonusPerStat * me.STAT_WEIGHTS[stat];
        });

        // Nếu đủ điểm → train bình thường
        // Nếu không đủ → chia đều điểm còn lại theo trọng số
        var actualBonusMap = {};
        if (totalWeightedCost <= remaining) {
            // Đủ điểm
            chosen.forEach(function (stat) {
                actualBonusMap[stat] = bonusPerStat;
            });
        } else {
            // Không đủ: chia remaining theo tỉ lệ trọng số
            var totalWeight = 0;
            chosen.forEach(function (stat) { totalWeight += me.STAT_WEIGHTS[stat]; });

            chosen.forEach(function (stat) {
                var share = (me.STAT_WEIGHTS[stat] / totalWeight) * remaining;
                // Số bậc thực tế = share / weight, làm tròn xuống tối thiểu 0
                var bac = Math.max(0, Math.floor(share / me.STAT_WEIGHTS[stat]));
                actualBonusMap[stat] = bac;
            });
        }

        chosen.forEach(function (stat) {
            var bonus  = actualBonusMap[stat] || 0;
            if (bonus <= 0) return;
            var oldVal = me._current[stat] || 0;
            var newVal = Math.min(100, oldVal + bonus);
            var actualBonus = newVal - oldVal;
            if (actualBonus <= 0) return;

            me._current[stat] = newVal;
            changes.push(stat.toUpperCase() + " +" + actualBonus);
        });

        // Tiêu hết điểm còn lại (dù có cộng chỉ số hay không)
        // để budget đạt max khi không đủ 1 bậc
        var usedAfter = me._calcUsedWeightedFromBase();
        if (usedAfter < me._maxPoints && totalWeightedCost > remaining) {
            // Còn điểm lẻ chưa tiêu — đẩy vào _usedExtra để đạt max
            me._usedExtra = (me._usedExtra || 0) + (me._maxPoints - usedAfter);
        }

        me._syncNormalStatCells();
        me._updateDisplay();

        // Hiển thị toast
        var msg = changes.length > 0
            ? "Coach applied! [" + changes.join(", ") + "]"
            : "No stats changed.";
        if (breakthrough) msg += " &nbsp;⚡ <b>BREAKTHROUGH!</b>";
        Ext.toast({ html: msg, align: "b", slideInDuration: 200, minWidth: 220 });
    },

    // ── Coach toggle handlers ─────────────────────────────────
    onCoachTypeToggle: function () {
        this._updateCoachInfoLabel();
    },

    onCoachTierToggle: function () {
        this._updateCoachInfoLabel();
    },

    _updateCoachInfoLabel: function () {
        var me = this;
        var label = me.lookupReference("coachInfoLabel");
        if (!label) return;
        var tier       = me._getSelectedTier();
        var type       = me._getSelectedType();
        var tierConfig = me.COACH_TIERS[tier];
        var typeStats  = me.COACH_TYPES[type];
        if (!tierConfig || !typeStats) return;
        var statsStr = typeStats.map(function (s) { return s.toUpperCase(); }).join(", ");
        var breakPct = (tierConfig.breakChance * 100) + "%";
        label.setHtml(
            "<div style='font-size:11px;color:#555;text-align:center'>" +
            "<b>" + tier.charAt(0).toUpperCase() + tier.slice(1) + "</b>: " +
            "+" + tierConfig.bonus + " to " + tierConfig.count + " stat(s) [" + statsStr + "]" +
            " &nbsp;|&nbsp; " + breakPct + " breakthrough (+" + (tierConfig.bonus + 1) + " each)" +
            "</div>"
        );
    },

    // ── Helpers: get selected coach type/tier ────────────────
    _getSelectedType: function () {
        var me = this;
        var btnFitness = me.lookupReference("btnFitness");
        if (btnFitness && btnFitness.pressed) return "fitness";
        return "technical";
    },

    _getSelectedTier: function () {
        var me = this;
        if (me.lookupReference("btnLegendary") && me.lookupReference("btnLegendary").pressed) return "legendary";
        if (me.lookupReference("btnRare")      && me.lookupReference("btnRare").pressed)      return "rare";
        return "common";
    },

    // ── Build stat cells (Custom mode, with arrows) ───────────
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

    // ── Build normal stat cells (Normal mode, no arrows) ──────
    _buildNormalStatCells: function () {
        var me = this;
        var normalStatsGrid = me.lookupReference("normalStatsGrid");
        if (!normalStatsGrid) return;
        var row1 = normalStatsGrid.down("#normalStatsRow1");
        var row2 = normalStatsGrid.down("#normalStatsRow2");
        if (!row1 || !row2) return;
        row1.removeAll(true);
        row2.removeAll(true);

        // Row 1: SPE ACC STA STR, Row 2: CON PAS SHO TAC
        var row1Stats = ["spe", "acc", "sta", "str"];
        var row2Stats = ["con", "pas", "sho", "tac"];

        row1Stats.forEach(function (stat) { row1.add(me._makeNormalStatCell(stat)); });
        row2Stats.forEach(function (stat) { row2.add(me._makeNormalStatCell(stat)); });
    },

    _makeNormalStatCell: function (stat) {
        var me = this;
        var label  = me.STAT_LABELS[stat];
        var weight = me.STAT_WEIGHTS[stat];
        var weightBadge = weight !== 1
            ? "<span style='font-size:9px;color:#f1c40f;margin-left:2px'>×" + weight + "</span>"
            : "";

        return {
            xtype: "container",
            itemId: "normal_cell_" + stat,
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
                // Value circle (canvas only, no arrows)
                {
                    xtype: "component",
                    itemId: "normal_canvas_" + stat,
                    html: '<canvas id="normal-stat-canvas-' + stat + '" width="56" height="56"></canvas>',
                },
                // Delta badge
                {
                    xtype: "component",
                    itemId: "normal_delta_" + stat,
                    html: "&nbsp;",
                    margin: "3 0 0 0",
                    style: { textAlign: "center", minHeight: "16px" },
                },
            ],
        };
    },

    // ── Adjust stat (Custom mode) ─────────────────────────────
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

    // Chỉ tính từ stat diffs (không có extra)
    _calcUsedWeightedFromBase: function () {
        var me = this;
        var total = 0;
        me.STATS.forEach(function (stat) {
            var diff = (me._current[stat] || 0) - (me._player[stat] || 0);
            total += diff * me.STAT_WEIGHTS[stat];
        });
        return total;
    },

    // ── Sync stat cell canvases (Custom mode) ─────────────────
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

    // ── Sync normal stat cell canvases (Normal mode) ──────────
    _syncNormalStatCells: function () {
        var me = this;
        me.STATS.forEach(function (stat) {
            me._drawNormalStatCircle(stat);
            me._updateNormalDelta(stat);
        });
    },

    _drawNormalStatCircle: function (stat) {
        var me = this;
        var val    = me._current[stat] || 0;
        var base   = me._player[stat]  || 0;
        var canvas = document.getElementById("normal-stat-canvas-" + stat);
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

    _updateNormalDelta: function (stat) {
        var me = this;
        var normalStatsGrid = me.lookupReference("normalStatsGrid");
        if (!normalStatsGrid) return;
        var deltaCmp = normalStatsGrid.down("#normal_delta_" + stat);
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
        var used    = Math.min(me._calcUsedWeighted(), me._maxPoints); // clamp không vượt max
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
        me._syncNormalStatCells();
    },

    _drawOvrCircle: function (dispOvr, baseOvr, used, max) {
        var canvas = document.getElementById("upgrade-ovr-canvas");
        if (!canvas) return;
        var ctx = canvas.getContext("2d");
        var W = 140, H = 140, cx = W / 2, cy = H / 2, R = 58;

        ctx.clearRect(0, 0, W, H);

        // Màu nền theo ngưỡng OVR
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
