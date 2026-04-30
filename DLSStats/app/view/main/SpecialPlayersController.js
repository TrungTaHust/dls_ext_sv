Ext.define("DLSStats.view.main.SpecialPlayersController", {
    extend: "Ext.app.ViewController",
    alias: "controller.specialplayers",

    onPlayerSelect: function (dataview, record) {
        this.showPlayerDetails(record.data);
    },

    showPlayerDetails: function (player) {
        var detailPanel = this.lookupReference("playerdetails");
        if (detailPanel) detailPanel.updatePlayer(player);
    },
});