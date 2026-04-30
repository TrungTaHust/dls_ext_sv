Ext.define("DLSStats.view.main.CompareController", {
    extend: "Ext.app.ViewController",
    alias: "controller.compare",

    // Số slot đang hiển thị (2, 3 hoặc 4)
    _slotCount: 2,

    onAddPlayer: function () {
        var me = this;
        if (me._slotCount >= 4) return;
        me._slotCount++;
        me._syncSlotVisibility();
    },

    onRemovePlayer: function () {
        var me = this;
        if (me._slotCount <= 2) return;
        // Xoá trắng slot vừa ẩn đi
        var input = me.getView().lookupReference("inputContainer");
        input.down("#player" + me._slotCount + "Id").setValue("");
        input.down("#version" + me._slotCount).setValue(null);
        me._slotCount--;
        me._syncSlotVisibility();
    },

    _syncSlotVisibility: function () {
        var me = this;
        var view = me.getView();
        var input = view.lookupReference("inputContainer");

        // Hiện/ẩn slot 3 và 4
        [3, 4].forEach(function (n) {
            var show = n <= me._slotCount;
            input.down("#player" + n + "Id").setVisible(show);
            input.down("#version" + n).setVisible(show);
        });

        // Nút "+ Add Player": ẩn khi đã đủ 4
        view.lookupReference("addPlayerBtn").setVisible(me._slotCount < 4);
        // Nút "- Remove Player": hiện khi > 2
        view.lookupReference("removePlayerBtn").setVisible(me._slotCount > 2);
    },

    onCompare: function () {
        var me = this;
        var view = me.getView();
        var input = view.lookupReference("inputContainer");
        var app = Ext.app.Application.instance;
        var stats = ["spe", "acc", "sta", "str", "con", "pas", "sho", "tac"];
        var statLabels = ["SPE", "ACC", "STA", "STR", "CON", "PAS", "SHO", "TAC"];
        var detailRefs = ["player1DetailsCmp", "player2DetailsCmp", "player3DetailsCmp", "player4DetailsCmp"];

        // Chỉ đọc đúng số slot đang hiện
        var players = [];
        for (var i = 1; i <= me._slotCount; i++) {
            var id = input.down("#player" + i + "Id").getValue();
            var ver = input.down("#version" + i).getValue();
            if (!id || !ver) continue;
            var results = app.searchPlayersByCriteria({ id: String(id), version: String(ver) }, null);
            if (results.length > 0) players.push(results[0].data);
        }

        if (players.length < 2) {
            Ext.Msg.alert("Not Found", "Please enter at least 2 valid player ID + version combinations.");
            return;
        }

        // Show/hide detail panels
        detailRefs.forEach(function (ref, idx) {
            var cmp = view.lookupReference(ref);
            if (idx < players.length) {
                cmp.setVisible(true);
                cmp.updatePlayer(players[idx]);
            } else {
                cmp.setVisible(false);
            }
        });

        // Radar chart — chỉ hiển thị khi so sánh đúng 2 người
        var radarChart = view.lookupReference("radarChartCmp");
        if (players.length === 2) {
            radarChart.setVisible(true);
            radarChart.updatePlayers(players);
        } else {
            radarChart.setVisible(false);
        }

        // Build stat highlight table
        me.buildStatTable(players, stats, statLabels);
    },

    buildStatTable: function (players, stats, statLabels) {
        var view = this.getView();
        var statTable = view.lookupReference("statTable");
        var statHtml = view.lookupReference("statTableHtml");

        // Header colors for up to 4 players
        var headerColors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"];
        var names = players.map(function (p) { return p.fname + " " + p.lname; });

        var html = '<table style="border-collapse:collapse;background:rgba(255,255,255,0.9);border-radius:8px;overflow:hidden;min-width:400px">';

        // Header row
        html += "<tr><th style='padding:8px 14px;background:#333;color:#fff'>Stat</th>";
        names.forEach(function (name, i) {
            html += "<th style='padding:8px 14px;background:" + headerColors[i] + ";color:#fff'>" + name + "</th>";
        });
        html += "</tr>";

        // Stat rows
        stats.forEach(function (stat, idx) {
            var values = players.map(function (p) { return parseInt(p[stat]) || 0; });
            var maxVal = Math.max.apply(null, values);
            var minVal = Math.min.apply(null, values);

            html += "<tr>";
            html += "<td style='padding:7px 14px;font-weight:bold;background:#f5f5f5;border-bottom:1px solid #ddd'>" + statLabels[idx] + "</td>";

            values.forEach(function (val) {
                var bg = "#fff";
                var color = "#333";
                if (players.length > 1) {
                    if (val === maxVal && maxVal !== minVal) { bg = "#d4edda"; color = "#155724"; }
                    else if (val === minVal && maxVal !== minVal) { bg = "#f8d7da"; color = "#721c24"; }
                }
                html += "<td style='padding:7px 14px;text-align:center;font-weight:bold;background:" + bg + ";color:" + color + ";border-bottom:1px solid #ddd'>" + val + "</td>";
            });

            html += "</tr>";
        });

        // Rating row
        var ratings = players.map(function (p) { return parseInt(p.rate) || 0; });
        var maxRating = Math.max.apply(null, ratings);
        var minRating = Math.min.apply(null, ratings);
        html += "<tr><td style='padding:7px 14px;font-weight:bold;background:#e9ecef;border-top:2px solid #aaa'>OVR</td>";
        ratings.forEach(function (val) {
            var bg = "#e9ecef";
            var color = "#333";
            if (players.length > 1) {
                if (val === maxRating && maxRating !== minRating) { bg = "#d4edda"; color = "#155724"; }
                else if (val === minRating && maxRating !== minRating) { bg = "#f8d7da"; color = "#721c24"; }
            }
            html += "<td style='padding:7px 14px;text-align:center;font-weight:bold;background:" + bg + ";color:" + color + ";border-top:2px solid #aaa'>" + val + "</td>";
        });
        html += "</tr></table>";

        statHtml.setHtml(html);
        statTable.setVisible(true);
    },
});