Ext.define("DLSStats.view.main.TeamShowcaseController", {
    extend: "Ext.app.ViewController",
    alias: "controller.teamshowcase",

    requires: ["DLSStats.util.PositionGroups"],

    FORMATIONS: null,
    _formationsData: null,

    init: function () {
        var me = this;
        me.FORMATIONS = Ext.ClassManager.get("DLSStats.view.main.BestXIController").prototype.FORMATIONS;

        // Load formations.json
        Ext.Ajax.request({
            url: "resources/data/formations.json",
            success: function (response) {
                me._formationsData = Ext.decode(response.responseText);
            },
            failure: function () {
                console.error("Failed to load formations.json");
            },
        });

        // Render pitch + populate combos sau khi view render xong
        me.getView().on("afterrender", function () {
            me._renderPitch("4-3-3", {});
            me._populateCombos();
        }, me, { single: true });
    },

    // Tính version mới nhất từ store — so sánh number để chắc chắn
    _getLatestVersion: function () {
        var latest = null;
        var playerStore = Ext.getStore("playerstore");
        if (!playerStore) return null;
        playerStore.each(function (rec) {
            var ver = parseInt(rec.get("version"), 10);
            if (isNaN(ver)) return;
            if (latest === null || ver > latest) latest = ver;
        });
        return latest !== null ? String(latest) : null;
    },

    // Populate combos chỉ với nation/club có >= 19 cầu thủ ở version mới nhất
    _populateCombos: function () {
        var me = this;
        var playerStore = Ext.getStore("playerstore");
        if (!playerStore) return;

        var doIt = function () {
            var latestVersion = me._getLatestVersion();
            if (!latestVersion) return;
            var latestVersionNum = parseInt(latestVersion, 10);

            var natCount = {}, clubCount = {};
            playerStore.each(function (rec) {
                if (parseInt(rec.get("version"), 10) !== latestVersionNum) return;
                var nat = rec.get("nat");
                var club = rec.get("club");
                if (nat) natCount[nat] = (natCount[nat] || 0) + 1;
                if (club) clubCount[club] = (clubCount[club] || 0) + 1;
            });

            var MIN = 19;
            var nations = Object.keys(natCount)
                .filter(function (n) { return natCount[n] >= MIN; })
                .sort()
                .map(function (n) { return { name: n }; });
            var clubs = Object.keys(clubCount)
                .filter(function (c) { return clubCount[c] >= MIN; })
                .sort()
                .map(function (c) { return { name: c }; });

            var nationCombo = me.lookupReference("nationCombo");
            var clubCombo = me.lookupReference("clubCombo");
            if (nationCombo) nationCombo.getStore().loadData(nations);
            if (clubCombo) clubCombo.getStore().loadData(clubs);
        };

        if (playerStore.isLoaded()) {
            doIt();
        } else {
            playerStore.on("load", doIt, me, { single: true });
        }
    },

    onModeToggle: function (container, button, pressed) {
        if (!pressed) return;
        var isNation = button.getText() === "Nation";
        this.lookupReference("nationCombo").setVisible(isNation);
        this.lookupReference("clubCombo").setVisible(!isNation);
        this.lookupReference("infoLabel").setHtml("");
        this._renderPitch("4-3-3", {});
        this._renderBench([]);
    },

    onCriteriaSelect: function (combo, record) {
        var me = this;
        var PG = DLSStats.util.PositionGroups;
        var value = record.get("name");

        // Kiểm tra combo nào đang hiện để xác định mode
        var isNation = me.lookupReference("nationCombo").isVisible();

        var playerStore = Ext.getStore("playerstore");
        if (!playerStore || !playerStore.isLoaded()) {
            Ext.Msg.alert("Error", "Player store not loaded yet.");
            return;
        }

        // Tính version mới nhất — version là number trong store, ép về number để so sánh đúng
        var latestVersion = me._getLatestVersion();
        if (!latestVersion) {
            Ext.Msg.alert("Error", "Could not determine latest version.");
            return;
        }

        var candidates = [];
        var latestVersionNum = parseInt(latestVersion, 10);
        playerStore.each(function (rec) {
            if (parseInt(rec.get("version"), 10) !== latestVersionNum) return;
            var match = isNation ? rec.get("nat") === value : rec.get("club") === value;
            if (!match) return;
            candidates.push(rec);
        });

        if (candidates.length < 19) {
            Ext.Msg.alert("Not Available", value + " does not have enough players (< 19) in the latest version.");
            return;
        }

        candidates.sort(function (a, b) { return b.get("rate") - a.get("rate"); });

        // Lấy formation từ formations.json, fallback 4-3-3
        var formation = "4-3-3";
        if (me._formationsData) {
            var map = isNation ? me._formationsData.nations : me._formationsData.clubs;
            if (map && map[value]) formation = map[value];
        }
        var slots = me.FORMATIONS[formation];

        var usedIds = {};
        var assigned = {};

        function pickBest(condFn, slotPos) {
            var sorted = PG.sortCandidates(
                candidates.filter(function (rec) { return !usedIds[String(rec.get("id"))]; }),
                slotPos
            );
            for (var i = 0; i < sorted.length; i++) {
                var rec = sorted[i];
                if (condFn(rec)) {
                    usedIds[String(rec.get("id"))] = true;
                    return rec.data;
                }
            }
            return null;
        }

        // Pass 1: exact position
        slots.forEach(function (slot, idx) {
            var p = pickBest(function (rec) { return rec.get("pos") === slot.pos; }, slot.pos);
            if (p) assigned[idx] = p;
        });

        // Pass 2: same group
        slots.forEach(function (slot, idx) {
            if (assigned[idx]) return;
            var p = pickBest(function (rec) { return PG.canPlay(rec.get("pos"), slot.pos); }, slot.pos);
            if (p) assigned[idx] = p;
        });

        // Pass 3: any player (guarantee 11)
        slots.forEach(function (slot, idx) {
            if (assigned[idx]) return;
            var p = pickBest(function () { return true; }, slot.pos);
            if (p) assigned[idx] = p;
        });

        // Pass 4: upgrade — same group + >= 2 rating better
        slots.forEach(function (slot, idx) {
            if (!assigned[idx]) return;
            var currentRate = parseInt(assigned[idx].rate) || 0;
            for (var i = 0; i < candidates.length; i++) {
                var rec = candidates[i];
                if (usedIds[String(rec.get("id"))]) continue;
                if (!PG.canPlay(rec.get("pos"), slot.pos)) continue;
                if ((rec.get("rate") - currentRate) >= 2) {
                    delete usedIds[String(assigned[idx].id)];
                    usedIds[String(rec.get("id"))] = true;
                    assigned[idx] = rec.data;
                    currentRate = rec.get("rate");
                }
            }
        });

        // Bench: 8 best unused
        var bench = [];
        for (var i = 0; i < candidates.length && bench.length < 8; i++) {
            var rec = candidates[i];
            if (!usedIds[String(rec.get("id"))]) {
                bench.push(rec.data);
                usedIds[String(rec.get("id"))] = true;
            }
        }

        var total = 0, count = 0;
        Ext.Object.each(assigned, function (k, p) { total += parseInt(p.rate) || 0; count++; });
        var avg = count > 0 ? (total / count).toFixed(1) : "-";

        me.lookupReference("infoLabel").setHtml(
            "<b>" + value + "</b> &nbsp;|&nbsp; <b>" + formation + "</b>" +
            " &nbsp;|&nbsp; Ver: <b>" + latestVersion + "</b>" +
            " &nbsp;|&nbsp; Avg: <b style='color:#f1c40f'>" + avg + "</b>" +
            " &nbsp;| Bench: <b style='color:#f1c40f'>" + bench.length + "</b>"
        );

        me._renderPitch(formation, assigned);
        me._renderBench(bench);
    },

    showPlayerDetail: function (key) {
        var detail = this.lookupReference("showcasePlayerDetails");
        if (!detail || !this._playerMap) return;
        var player = this._playerMap[key];
        if (player) detail.updatePlayer(player);
    },

    _renderPitch: function (formation, assigned) {
        var me = this;
        // Reset player map mỗi lần render
        if (!me._playerMap) me._playerMap = {};

        var pitchCmp = me.lookupReference("showcasePitch");
        if (!pitchCmp || !pitchCmp.rendered) return;
        var pitchEl = pitchCmp.el.down("#dls-showcase-pitch-inner");
        if (!pitchEl) return;

        var slots = me.FORMATIONS[formation];
        if (!slots) return;

        var linesHtml = [
            '<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:100px;height:100px;border:2px solid rgba(255,255,255,0.4);border-radius:50%"></div>',
            '<div style="position:absolute;left:5%;top:50%;width:90%;height:2px;background:rgba(255,255,255,0.3)"></div>',
            '<div style="position:absolute;left:20%;top:2%;width:60%;height:18%;border:2px solid rgba(255,255,255,0.3)"></div>',
            '<div style="position:absolute;left:20%;bottom:2%;width:60%;height:18%;border:2px solid rgba(255,255,255,0.3)"></div>',
        ].join("");

        var slotsHtml = slots.map(function (slot, idx) {
            var player = assigned[idx];
            var label = player ? (player.fname ? player.fname.charAt(0) + "." + player.lname : player.lname) : slot.pos;
            var rating = player ? player.rate : "";
            var bg, border, textColor;
            if (player) {
                var rate = parseInt(player.rate) || 0;
                if (rate >= 80) { bg = "#f1c40f"; border = "2px solid #000"; }
                else if (rate >= 70) { bg = "#2980b9"; border = "2px solid #000"; }
                else { bg = "#b87333"; border = "2px solid #000"; }
                textColor = "#000";
            } else {
                bg = "rgba(255,0,0,0.5)"; border = "2px dashed #fff"; textColor = "#fff";
            }
            var clickAttr = "";
            if (player) {
                var key = "slot_" + idx;
                me._playerMap[key] = player;
                clickAttr = 'onclick="Ext.ComponentQuery.query(\'dls-teamshowcase\')[0].getController().showPlayerDetail(\'' + key + '\')"';
            }
            return '<div ' + clickAttr + ' style="position:absolute;left:' + slot.x + '%;top:' + slot.y + '%;' +
                'transform:translate(-50%,-50%);width:64px;height:64px;border-radius:50%;' +
                'background:' + bg + ';border:' + border + ';' +
                'display:flex;flex-direction:column;align-items:center;justify-content:center;' +
                'text-align:center;color:' + textColor + ';font-size:10px;font-weight:bold;' +
                'box-shadow:0 2px 6px rgba(0,0,0,0.4);' + (player ? 'cursor:pointer;' : '') + '">' +
                '<span style="font-size:9px">' + (player ? player.pos : slot.pos) + '</span>' +
                '<span style="font-size:11px;max-width:58px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">' + label + '</span>' +
                (rating ? '<span style="font-size:12px">' + rating + '</span>' : '') +
                '</div>';
        }).join("");

        pitchEl.setHtml(linesHtml + slotsHtml);
    },

    _renderBench: function (bench) {
        var me = this;
        var benchCmp = me.lookupReference("benchPanel");
        if (!benchCmp || !benchCmp.rendered) return;
        var benchEl = benchCmp.el.down("#dls-showcase-bench");
        if (!benchEl) return;

        if (!me._playerMap) me._playerMap = {};

        var header = '<div style="color:#fff;font-weight:bold;text-align:center;font-size:13px;' +
            'margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.4);padding-bottom:6px">SUBSTITUTES</div>';

        if (bench.length === 0) { benchEl.setHtml(header); return; }

        var rows = bench.map(function (p, idx) {
            var rate = parseInt(p.rate) || 0;
            var bg = rate >= 80 ? "#f1c40f" : rate >= 70 ? "#2980b9" : "#b87333";
            var color = "#000";
            var name = (p.fname ? p.fname.charAt(0) + "." : "") + p.lname;
            var key = "bench_" + idx;
            me._playerMap[key] = p;
            return '<div onclick="Ext.ComponentQuery.query(\'dls-teamshowcase\')[0].getController().showPlayerDetail(\'' + key + '\')" ' +
                'style="display:flex;align-items:center;margin-bottom:6px;background:rgba(255,255,255,0.08);border-radius:6px;padding:4px 6px;cursor:pointer;">' +
                '<div style="width:28px;height:28px;border-radius:50%;background:' + bg + ';display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:11px;color:' + color + ';flex-shrink:0">' + rate + '</div>' +
                '<div style="margin-left:6px;overflow:hidden">' +
                '<div style="color:#fff;font-size:11px;font-weight:bold;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:130px">' + name + '</div>' +
                '<div style="color:rgba(255,255,255,0.6);font-size:10px">' + p.pos + '</div>' +
                '</div></div>';
        }).join("");

        benchEl.setHtml(header + rows);
    },
});
