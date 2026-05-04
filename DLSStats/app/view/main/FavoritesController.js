Ext.define("DLSStats.view.main.FavoritesController", {
    extend: "Ext.app.ViewController",
    alias: "controller.favorites",

    STORAGE_KEY: "dls_favorites",
    ITEMS_PER_PAGE: 10,

    _currentPage: 1,

    init: function () {
        this._currentPage = 1;
        this.loadFromStorage();
    },

    getFavorites: function () {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || "[]");
        } catch (e) {
            return [];
        }
    },

    saveFavorites: function (list) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(list));
    },

    loadFromStorage: function () {
        this._currentPage = 1;
        this._renderPage();
    },

    _renderPage: function () {
        var me = this;
        var all = me.getFavorites();
        var total = all.length;
        var perPage = me.ITEMS_PER_PAGE;
        var page = me._currentPage;
        var totalPages = Math.max(1, Math.ceil(total / perPage));

        // Clamp page
        if (page < 1) page = 1;
        if (page > totalPages) page = totalPages;
        me._currentPage = page;

        var start = (page - 1) * perPage;
        var pageData = all.slice(start, start + perPage);

        var grid = me.lookupReference("favoritesGrid");
        if (grid) grid.getStore().loadData(pageData);

        // Update paging controls
        var prevBtn = me.lookupReference("favPrevBtn");
        var nextBtn = me.lookupReference("favNextBtn");
        var label  = me.lookupReference("favPageLabel");

        if (prevBtn) prevBtn.setDisabled(page <= 1);
        if (nextBtn) nextBtn.setDisabled(page >= totalPages);
        if (label) {
            label.setHtml(
                total > 0
                    ? "<span style='color:#333;font-weight:bold'>" + page + " / " + totalPages + " (" + total + ")</span>"
                    : "<span style='color:#999'>No favorites</span>"
            );
        }
    },

    addFavorite: function (player) {
        var list = this.getFavorites();
        var uid = player.id + "_" + player.version;
        var exists = Ext.Array.some(list, function (p) {
            return p.id + "_" + p.version === uid;
        });
        if (exists) {
            Ext.Msg.alert("Info", player.fname + " " + player.lname + " is already in Favorites.");
            return;
        }
        list.push(player);
        this.saveFavorites(list);
        // Nhảy đến trang cuối để thấy player vừa thêm
        var total = list.length;
        this._currentPage = Math.ceil(total / this.ITEMS_PER_PAGE);
        this._renderPage();
        Ext.Msg.alert("Added", player.fname + " " + player.lname + " added to Favorites!");
    },

    onRemoveFavorite: function (grid, rowIndex) {
        var rec = grid.getStore().getAt(rowIndex);
        if (!rec) return;
        var uid = rec.get("id") + "_" + rec.get("version");
        var list = Ext.Array.filter(this.getFavorites(), function (p) {
            return p.id + "_" + p.version !== uid;
        });
        this.saveFavorites(list);
        this._renderPage();
    },

    onClearAll: function () {
        Ext.Msg.confirm("Clear All", "Remove all favorites?", function (btn) {
            if (btn === "yes") {
                this.saveFavorites([]);
                this._currentPage = 1;
                this._renderPage();
            }
        }, this);
    },

    onFavPrev: function () {
        this._currentPage--;
        this._renderPage();
    },

    onFavNext: function () {
        this._currentPage++;
        this._renderPage();
    },

    onFavoriteSelect: function (grid, record) {
        var detail = this.lookupReference("playerdetails");
        if (detail) detail.updatePlayer(record.data);
    },
});
