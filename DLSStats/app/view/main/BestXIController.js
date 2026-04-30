Ext.define("DLSStats.view.main.BestXIController", {
    extend: "Ext.app.ViewController",
    alias: "controller.bestxi",

    requires: ["DLSStats.util.PositionGroups"],

    FORMATIONS: {
        "4-3-3": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "CM", x: 25, y: 52 }, { pos: "CM", x: 50, y: 52 }, { pos: "CM", x: 75, y: 52 }, { pos: "LW", x: 15, y: 28 }, { pos: "CF", x: 50, y: 18 }, { pos: "RW", x: 85, y: 28 }],
        "4-2-3-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "DM", x: 35, y: 55 }, { pos: "DM", x: 65, y: 55 }, { pos: "LM", x: 15, y: 38 }, { pos: "AM", x: 50, y: 38 }, { pos: "RM", x: 85, y: 38 }, { pos: "CF", x: 50, y: 18 }],
        "4-5-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "LM", x: 10, y: 50 }, { pos: "CM", x: 30, y: 50 }, { pos: "CM", x: 50, y: 50 }, { pos: "CM", x: 70, y: 50 }, { pos: "RM", x: 90, y: 50 }, { pos: "CF", x: 50, y: 18 }],
        "4-1-4-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "DM", x: 50, y: 60 }, { pos: "LM", x: 12, y: 42 }, { pos: "CM", x: 35, y: 42 }, { pos: "CM", x: 65, y: 42 }, { pos: "RM", x: 88, y: 42 }, { pos: "CF", x: 50, y: 18 }],
        "4-3-2-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "CM", x: 25, y: 55 }, { pos: "CM", x: 50, y: 55 }, { pos: "CM", x: 75, y: 55 }, { pos: "SS", x: 33, y: 32 }, { pos: "SS", x: 67, y: 32 }, { pos: "CF", x: 50, y: 15 }],
        "4-4-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "LM", x: 12, y: 50 }, { pos: "CM", x: 35, y: 50 }, { pos: "CM", x: 65, y: 50 }, { pos: "RM", x: 88, y: 50 }, { pos: "CF", x: 35, y: 20 }, { pos: "CF", x: 65, y: 20 }],
        "4-3-1-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "CM", x: 25, y: 55 }, { pos: "CM", x: 50, y: 55 }, { pos: "CM", x: 75, y: 55 }, { pos: "AM", x: 50, y: 38 }, { pos: "CF", x: 35, y: 20 }, { pos: "CF", x: 65, y: 20 }],
        "4-1-2-1-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "DM", x: 50, y: 62 }, { pos: "CM", x: 28, y: 48 }, { pos: "CM", x: 72, y: 48 }, { pos: "AM", x: 50, y: 34 }, { pos: "CF", x: 35, y: 18 }, { pos: "CF", x: 65, y: 18 }],
        "4-1-3-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "DM", x: 50, y: 62 }, { pos: "LM", x: 18, y: 45 }, { pos: "CM", x: 50, y: 45 }, { pos: "RM", x: 82, y: 45 }, { pos: "CF", x: 35, y: 20 }, { pos: "CF", x: 65, y: 20 }],
        "4-2-2-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "DM", x: 35, y: 57 }, { pos: "DM", x: 65, y: 57 }, { pos: "LM", x: 20, y: 40 }, { pos: "RM", x: 80, y: 40 }, { pos: "CF", x: 35, y: 20 }, { pos: "CF", x: 65, y: 20 }],
        "4-4-1-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "LM", x: 12, y: 52 }, { pos: "CM", x: 35, y: 52 }, { pos: "CM", x: 65, y: 52 }, { pos: "RM", x: 88, y: 52 }, { pos: "SS", x: 50, y: 33 }, { pos: "CF", x: 50, y: 16 }],
        "4-1-2-3": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "DM", x: 50, y: 60 }, { pos: "CM", x: 30, y: 45 }, { pos: "CM", x: 70, y: 45 }, { pos: "LW", x: 15, y: 25 }, { pos: "CF", x: 50, y: 18 }, { pos: "RW", x: 85, y: 25 }],
        "4-2-1-3": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 15, y: 72 }, { pos: "CB", x: 35, y: 72 }, { pos: "CB", x: 65, y: 72 }, { pos: "RB", x: 85, y: 72 }, { pos: "DM", x: 33, y: 57 }, { pos: "DM", x: 67, y: 57 }, { pos: "AM", x: 50, y: 42 }, { pos: "LW", x: 15, y: 25 }, { pos: "CF", x: 50, y: 15 }, { pos: "RW", x: 85, y: 25 }],
        "5-3-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 8, y: 72 }, { pos: "CB", x: 27, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 73, y: 72 }, { pos: "RB", x: 92, y: 72 }, { pos: "CM", x: 25, y: 50 }, { pos: "CM", x: 50, y: 50 }, { pos: "CM", x: 75, y: 50 }, { pos: "CF", x: 35, y: 22 }, { pos: "CF", x: 65, y: 22 }],
        "5-2-1-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 8, y: 72 }, { pos: "CB", x: 27, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 73, y: 72 }, { pos: "RB", x: 92, y: 72 }, { pos: "CM", x: 33, y: 55 }, { pos: "CM", x: 67, y: 55 }, { pos: "AM", x: 50, y: 38 }, { pos: "CF", x: 33, y: 20 }, { pos: "CF", x: 67, y: 20 }],
        "5-2-3": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 8, y: 72 }, { pos: "CB", x: 27, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 73, y: 72 }, { pos: "RB", x: 92, y: 72 }, { pos: "CM", x: 33, y: 55 }, { pos: "CM", x: 67, y: 55 }, { pos: "LW", x: 15, y: 28 }, { pos: "CF", x: 50, y: 18 }, { pos: "RW", x: 85, y: 28 }],
        "5-2-2-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 8, y: 72 }, { pos: "CB", x: 27, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 73, y: 72 }, { pos: "RB", x: 92, y: 72 }, { pos: "CM", x: 33, y: 57 }, { pos: "CM", x: 67, y: 57 }, { pos: "LM", x: 22, y: 38 }, { pos: "RM", x: 78, y: 38 }, { pos: "CF", x: 50, y: 18 }],
        "5-4-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 8, y: 72 }, { pos: "CB", x: 27, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 73, y: 72 }, { pos: "RB", x: 92, y: 72 }, { pos: "LM", x: 12, y: 50 }, { pos: "CM", x: 35, y: 50 }, { pos: "CM", x: 65, y: 50 }, { pos: "RM", x: 88, y: 50 }, { pos: "CF", x: 50, y: 18 }],
        "5-1-2-1-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "LB", x: 8, y: 72 }, { pos: "CB", x: 27, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 73, y: 72 }, { pos: "RB", x: 92, y: 72 }, { pos: "DM", x: 50, y: 60 }, { pos: "CM", x: 30, y: 47 }, { pos: "CM", x: 70, y: 47 }, { pos: "AM", x: 50, y: 33 }, { pos: "CF", x: 50, y: 16 }],
        "3-5-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "LWB", x: 8, y: 50 }, { pos: "CM", x: 28, y: 50 }, { pos: "CM", x: 50, y: 50 }, { pos: "CM", x: 72, y: 50 }, { pos: "RWB", x: 92, y: 50 }, { pos: "CF", x: 35, y: 22 }, { pos: "CF", x: 65, y: 22 }],
        "3-2-3-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "DM", x: 33, y: 60 }, { pos: "DM", x: 67, y: 60 }, { pos: "LWB", x: 15, y: 42 }, { pos: "CM", x: 50, y: 42 }, { pos: "RWB", x: 85, y: 42 }, { pos: "CF", x: 35, y: 20 }, { pos: "CF", x: 65, y: 20 }],
        "3-4-1-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "LWB", x: 12, y: 55 }, { pos: "CM", x: 35, y: 55 }, { pos: "CM", x: 65, y: 55 }, { pos: "RWB", x: 88, y: 55 }, { pos: "AM", x: 50, y: 38 }, { pos: "CF", x: 35, y: 20 }, { pos: "CF", x: 65, y: 20 }],
        "3-1-4-2": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "DM", x: 50, y: 62 }, { pos: "LWB", x: 12, y: 47 }, { pos: "CM", x: 35, y: 47 }, { pos: "CM", x: 65, y: 47 }, { pos: "RWB", x: 88, y: 47 }, { pos: "CF", x: 35, y: 20 }, { pos: "CF", x: 65, y: 20 }],
        "3-5-1-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "LWB", x: 8, y: 52 }, { pos: "CM", x: 28, y: 52 }, { pos: "CM", x: 50, y: 52 }, { pos: "CM", x: 72, y: 52 }, { pos: "RWB", x: 92, y: 52 }, { pos: "SS", x: 50, y: 33 }, { pos: "CF", x: 50, y: 16 }],
        "3-4-3": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "LWB", x: 12, y: 55 }, { pos: "CM", x: 35, y: 55 }, { pos: "CM", x: 65, y: 55 }, { pos: "RWB", x: 88, y: 55 }, { pos: "LW", x: 15, y: 28 }, { pos: "CF", x: 50, y: 18 }, { pos: "RW", x: 85, y: 28 }],
        "3-4-2-1": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "LWB", x: 12, y: 57 }, { pos: "CM", x: 35, y: 57 }, { pos: "CM", x: 65, y: 57 }, { pos: "RWB", x: 88, y: 57 }, { pos: "SS", x: 33, y: 35 }, { pos: "SS", x: 67, y: 35 }, { pos: "CF", x: 50, y: 16 }],
        "3-3-1-3": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "CM", x: 25, y: 57 }, { pos: "CM", x: 50, y: 57 }, { pos: "CM", x: 75, y: 57 }, { pos: "AM", x: 50, y: 40 }, { pos: "LW", x: 15, y: 25 }, { pos: "CF", x: 50, y: 15 }, { pos: "RW", x: 85, y: 25 }],
        "3-1-2-1-3": [{ pos: "GK", x: 50, y: 88 }, { pos: "CB", x: 25, y: 72 }, { pos: "CB", x: 50, y: 72 }, { pos: "CB", x: 75, y: 72 }, { pos: "DM", x: 50, y: 62 }, { pos: "CM", x: 30, y: 50 }, { pos: "CM", x: 70, y: 50 }, { pos: "AM", x: 50, y: 37 }, { pos: "LW", x: 15, y: 23 }, { pos: "CF", x: 50, y: 14 }, { pos: "RW", x: 85, y: 23 }],
    },

    _slots: [],
    _assigned: {},
    _activeSlot: -1,

    init: function () {
        var me = this;
        var pitch = me.lookupReference("pitch");
        if (pitch) {
            pitch.on("afterrender", function () {
                me.renderFormation("4-3-3");
            }, me, { single: true });
        }
    },

    onAutoPick: function () {
        var me = this;
        var PG = DLSStats.util.PositionGroups;
        var formation = me.lookupReference("formationCombo").getValue();
        var slots = me.FORMATIONS[formation];
        if (!slots) return;

        var playerStore = Ext.getStore("playerstore");
        if (!playerStore || !playerStore.isLoaded()) {
            Ext.Msg.alert("Error", "Player store not loaded yet.");
            return;
        }

        var fNat = "";
        var fClub = "";
        var fFoot = "";
        var fHgt = 0;
        var fSpe = 0;
        var fAcc = 0;
        var fSta = 0;
        var fStr = 0;
        var fCon = 0;
        var fPas = 0;
        var fSho = 0;
        var fTac = 0;

        // Tìm version mới nhất có trong store (số lớn nhất)
        var latestVersion = null;
        playerStore.each(function (rec) {
            var ver = rec.get("version");
            if (latestVersion === null || ver > latestVersion) {
                latestVersion = ver;
            }
        });

        var candidates = [];
        playerStore.each(function (rec) {
            if (rec.get("version") !== latestVersion) return;
            if (fNat && rec.get("nat") !== fNat) return;
            if (fClub && rec.get("club") !== fClub) return;
            if (fFoot && rec.get("foot") !== fFoot) return;
            if (fHgt && rec.get("hgt") < fHgt) return;
            if (fSpe && rec.get("spe") < fSpe) return;
            if (fAcc && rec.get("acc") < fAcc) return;
            if (fSta && rec.get("sta") < fSta) return;
            if (fStr && rec.get("str") < fStr) return;
            if (fCon && rec.get("con") < fCon) return;
            if (fPas && rec.get("pas") < fPas) return;
            if (fSho && rec.get("sho") < fSho) return;
            if (fTac && rec.get("tac") < fTac) return;
            candidates.push(rec);
        });

        if (candidates.length === 0) {
            Ext.Msg.alert("No Results", "No players match the selected filters.");
            return;
        }

        candidates.sort(function (a, b) { return b.get("rate") - a.get("rate"); });

        var usedIds = {};
        var assigned = {};

        function pickBest(condFn, slotPos) {
            var sorted = DLSStats.util.PositionGroups.sortCandidates(
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

        function bestExactRating(slotPos) {
            for (var i = 0; i < candidates.length; i++) {
                var rec = candidates[i];
                if (!usedIds[String(rec.get("id"))] && rec.get("pos") === slotPos) {
                    return rec.get("rate");
                }
            }
            return -1;
        }

        // Pass 1: exact position
        slots.forEach(function (slot, idx) {
            var player = pickBest(function (rec) { return rec.get("pos") === slot.pos; }, slot.pos);
            if (player) assigned[idx] = player;
        });

        // Pass 2: same-group, only if no exact left or 4+ better
        slots.forEach(function (slot, idx) {
            if (assigned[idx]) return;
            var exactBest = bestExactRating(slot.pos);
            var player = pickBest(function (rec) {
                if (rec.get("pos") === slot.pos) return true;
                if (!PG.canPlay(rec.get("pos"), slot.pos)) return false;
                if (exactBest < 0) return true;
                return (rec.get("rate") - exactBest) >= 4;
            }, slot.pos);
            if (player) assigned[idx] = player;
        });

        var filledCount = Object.keys(assigned).length;
        if (filledCount < 11) {
            Ext.Msg.alert("Partial Result", "Only " + filledCount + "/11 slots could be filled. Try relaxing some filters.");
        }

        me._assigned = assigned;
        me.renderFormation(formation);
        me.updateTotalRating();
    },

    onFormationChange: function (combo) {
        this._assigned = {};
        this.renderFormation(combo.getValue());
        this.updateTotalRating();
    },

    onClearXI: function () {
        this._assigned = {};
        this.renderFormation(this.lookupReference("formationCombo").getValue());
        this.updateTotalRating();
    },

    renderFormation: function (formation) {
        var me = this;
        var slots = me.FORMATIONS[formation];
        if (!slots) return;
        me._slots = slots;

        var pitchCmp = me.lookupReference("pitch");
        if (!pitchCmp || !pitchCmp.rendered) return;
        var pitchEl = pitchCmp.el.down("#dls-pitch-inner");
        if (!pitchEl) return;

        var linesHtml = [
            '<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:100px;height:100px;border:2px solid rgba(255,255,255,0.4);border-radius:50%"></div>',
            '<div style="position:absolute;left:5%;top:50%;width:90%;height:2px;background:rgba(255,255,255,0.3)"></div>',
            '<div style="position:absolute;left:20%;top:2%;width:60%;height:18%;border:2px solid rgba(255,255,255,0.3)"></div>',
            '<div style="position:absolute;left:20%;bottom:2%;width:60%;height:18%;border:2px solid rgba(255,255,255,0.3)"></div>',
        ].join("");

        var slotsHtml = slots.map(function (slot, idx) {
            var player = me._assigned[idx];
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
                bg = "rgba(0,0,0,0.45)"; border = "2px dashed rgba(255,255,255,0.7)"; textColor = "#fff";
            }
            return '<div onclick="Ext.ComponentQuery.query(\'dls-bestxi\')[0].getController().onSlotClick(' + idx + ')" ' +
                'style="position:absolute;left:' + slot.x + '%;top:' + slot.y + '%;transform:translate(-50%,-50%);' +
                'width:64px;height:64px;border-radius:50%;background:' + bg + ';border:' + border + ';' +
                'display:flex;flex-direction:column;align-items:center;justify-content:center;' +
                'cursor:pointer;text-align:center;color:' + textColor + ';font-size:10px;font-weight:bold;' +
                'box-shadow:0 2px 6px rgba(0,0,0,0.4);transition:transform 0.15s">' +
                '<span style="font-size:9px">' + (player ? player.pos : slot.pos) + '</span>' +
                '<span style="font-size:11px;max-width:58px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">' + label + '</span>' +
                (rating ? '<span style="font-size:12px">' + rating + '</span>' : '') +
                '</div>';
        }).join("");

        pitchEl.setHtml(linesHtml + slotsHtml);
    },

    onSlotClick: function (slotIdx) {
        var me = this;
        me._activeSlot = slotIdx;

        if (!me._searchWin || me._searchWin.destroyed) {
            me._searchWin = Ext.create("Ext.window.Window", {
                title: "Select Player", width: 480, height: 380, modal: true,
                closeAction: "hide",  // hide thay vì destroy khi bấm X
                layout: "fit",
                items: [{
                    xtype: "container", layout: { type: "vbox", align: "stretch" }, padding: 8,
                    items: [
                        {
                            xtype: "textfield", itemId: "searchInput", emptyText: "Search by name...", enableKeyEvents: true,
                            listeners: { keyup: { fn: function () { me._doSearch(); }, buffer: 300 } },
                            margin: "0 0 8 0"
                        },
                        {
                            xtype: "grid", itemId: "searchResultGrid", flex: 1, columnLines: true,
                            store: { fields: ["fname", "lname", "pos", "rate", "id", "version", "nat", "club", "foot", "hgt", "spe", "acc", "sta", "str", "con", "pas", "sho", "tac", "prc"], data: [] },
                            columns: [
                                { text: "Name", flex: 2, renderer: function (v, m, rec) { return rec.get("fname") + " " + rec.get("lname"); } },
                                { text: "Pos", dataIndex: "pos", width: 55, align: "center" },
                                { text: "OVR", dataIndex: "rate", width: 55, align: "center" },
                                { text: "Ver", dataIndex: "version", width: 70, align: "center" },
                            ],
                            listeners: { itemdblclick: function (grid, record) { me._onPlayerPicked(record); } },
                        },
                    ],
                }],
            });
        }

        me._searchWin.down("#searchInput").setValue("");
        me._searchWin.down("#searchResultGrid").getStore().loadData([]);
        me._searchWin.show();
    },

    _doSearch: function () {
        var me = this;
        var term = me._searchWin.down("#searchInput").getValue().toLowerCase().trim();
        if (!term) { me._searchWin.down("#searchResultGrid").getStore().loadData([]); return; }
        var results = Ext.getStore("playerstore").queryBy(function (rec) {
            return (rec.get("fname") + " " + rec.get("lname")).toLowerCase().indexOf(term) !== -1;
        }).getRange();
        me._searchWin.down("#searchResultGrid").getStore().loadData(Ext.Array.map(results.slice(0, 50), function (r) { return r.data; }));
    },

    _onPlayerPicked: function (record) {
        if (this._activeSlot < 0) return;
        this._assigned[this._activeSlot] = record.data;
        this._searchWin.hide();
        this.renderFormation(this.lookupReference("formationCombo").getValue());
        this.updateTotalRating();
    },

    updateTotalRating: function () {
        var total = 0, count = 0;
        Ext.Object.each(this._assigned, function (k, p) { total += parseInt(p.rate) || 0; count++; });
        var display = count > 0 ? (total / count).toFixed(1) + " avg (" + count + "/11)" : "-";
        this.lookupReference("totalRating").setHtml(
            "<div style='" +
            "background:rgba(0,0,0,0.65);" +
            "border:2px solid rgba(255,255,255,0.3);" +
            "border-radius:8px;" +
            "padding:6px 16px;" +
            "color:#fff;" +
            "font-size:13px;" +
            "font-weight:bold;" +
            "text-shadow:0 1px 2px rgba(0,0,0,0.8);" +
            "white-space:nowrap;" +
            "'>Team Rating: <span style='color:#f1c40f;font-size:18px'>" + display + "</span></div>"
        );
    },
});