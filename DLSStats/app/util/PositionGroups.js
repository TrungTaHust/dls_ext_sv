Ext.define("DLSStats.util.PositionGroups", {
    singleton: true,

    GROUPS: [
        ["LB", "RB", "CB"],
        ["LB", "LWB", "RB", "RWB"],
        ["LM", "RM", "RWB", "LWB", "LW", "RW"],
        ["CM", "DM"],
        ["CM", "AM"],
        ["AM", "SS", "CF"],
        ["CF", "SS", "LW", "RW"],
    ],

    // Positions that prefer left-footed players
    LEFT_POS: ["LW", "LB", "LWB", "LM", "LCB"],
    // Positions that prefer right-footed players
    RIGHT_POS: ["RW", "RB", "RWB", "RM", "RCB"],

    canPlay: function (playerPos, slotPos) {
        // LCB and RCB are treated as CB for canPlay purposes
        var normSlot = (slotPos === "LCB" || slotPos === "RCB") ? "CB" : slotPos;
        var normPlayer = (playerPos === "LCB" || playerPos === "RCB") ? "CB" : playerPos;
        if (normPlayer === normSlot) return true;
        for (var i = 0; i < this.GROUPS.length; i++) {
            var g = this.GROUPS[i];
            if (g.indexOf(normPlayer) !== -1 && g.indexOf(normSlot) !== -1) return true;
        }
        return false;
    },

    // Returns a foot-preference score for sorting:
    // Higher = better fit for the slot
    // B foot always scores 3 (fits anywhere)
    // Preferred foot for L/R slots scores 2
    // Neutral slot (no L/R preference): B=3, L=2, R=1
    footScore: function (foot, slotPos) {
        if (foot === "B") return 3;
        var isLeftSlot = this.LEFT_POS.indexOf(slotPos) !== -1;
        var isRightSlot = this.RIGHT_POS.indexOf(slotPos) !== -1;
        if (isLeftSlot) return foot === "L" ? 2 : 0;
        if (isRightSlot) return foot === "R" ? 2 : 0;
        // Neutral slot: L preferred over R
        return foot === "L" ? 2 : 1;
    },

    // Sort candidates by: rating DESC, then footScore DESC
    sortCandidates: function (candidates, slotPos) {
        var me = this;
        return candidates.slice().sort(function (a, b) {
            var rDiff = b.get("rate") - a.get("rate");
            if (rDiff !== 0) return rDiff;
            return me.footScore(b.get("foot"), slotPos) - me.footScore(a.get("foot"), slotPos);
        });
    },
});


