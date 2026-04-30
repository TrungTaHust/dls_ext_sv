Ext.define("DLSStats.view.main.MainSearchController", {
    extend: "Ext.app.ViewController",
    alias: "controller.mainsearch",

    config: {
        currentPage: 1,
        itemsPerPage: 10,
        currentResults: [],
    },

    control: {
        "dls-searchform": {
            searchrequest: "onSearch",
        },
    },

    fireSearch: function () {
        var form = Ext.ComponentQuery.query("dls-searchform")[0];
        if (form) form.fireEvent("searchrequest", form.getValues());
    },

    onTextFieldChange: function () {
        this.fireSearch();
    },

    onComboSelect: function () {
        this.fireSearch();
    },

    onSearch: function (values) {
        var me = this;
        var playerStore = Ext.getStore("playerstore");

        if (!playerStore) return;

        if (!playerStore.isLoaded()) {
            playerStore.on("load", function () { me.onSearch(values); }, { single: true });
            return;
        }

        var criteria = {};
        ["id", "nat", "club", "pos", "foot", "rate", "version"].forEach(function (key) {
            if (values[key]) criteria[key] = String(values[key]).toLowerCase();
        });

        var nameTerm = values.name ? values.name.toLowerCase() : null;
        var results = Ext.app.Application.instance.searchPlayersByCriteria(criteria, nameTerm);

        me.setCurrentResults(results);
        me.setCurrentPage(1);
        me.updatePaging();
        me.loadPage(1);
    },

    loadPage: function (page) {
        var vm = this.getViewModel();
        var start = (page - 1) * this.getItemsPerPage();
        var end = start + this.getItemsPerPage();
        var pageData = this.getCurrentResults().slice(start, end);

        vm.getStore("players").loadData(pageData);
        vm.set("hasPrev", page > 1);
        vm.set("hasNext", end < this.getCurrentResults().length);

        if (pageData.length > 0) {
            this.showPlayerDetails(pageData[0]);
        }
    },

    updatePaging: function () {
        var vm = this.getViewModel();
        var itemsPerPage = this.getItemsPerPage();
        vm.set("hasPrev", this.getCurrentPage() > 1);
        vm.set("hasNext", this.getCurrentPage() * itemsPerPage < this.getCurrentResults().length);
    },

    onNext: function () {
        var page = this.getCurrentPage() + 1;
        this.setCurrentPage(page);
        this.loadPage(page);
    },

    onBack: function () {
        var page = this.getCurrentPage() - 1;
        if (page >= 1) {
            this.setCurrentPage(page);
            this.loadPage(page);
        }
    },

    onPlayerSelect: function (dataview, record) {
        this.showPlayerDetails(record.data);
    },

    showPlayerDetails: function (player) {
        var detailPanel = this.lookupReference("playerdetails");
        if (detailPanel) detailPanel.updatePlayer(player);
    },
});