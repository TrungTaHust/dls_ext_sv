Ext.define("DLSStats.view.main.PlayerController", {
  extend: "Ext.app.ViewController",
  alias: "controller.player",

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

  init: function () {
    var form = this.lookup("searchform");
    if (form) form.on("searchrequest", this.onSearch, this);
  },

  searchPlayersByCriteria: function (criteria, nameTerm) {
    var playerStore = Ext.getStore("playerstore");
    if (!playerStore) {
      console.error("Không tìm thấy store playerstore");
      return [];
    }

    nameTerm = nameTerm ? nameTerm.toLowerCase() : null;

    var filteredRecords = playerStore.queryBy(function (record) {
      for (var key in criteria) {
        var value = record.get(key);
        if (value == null) return false;

        var criteriaValue = criteria[key];
        if (typeof value === "number") {
          if (value !== parseInt(criteriaValue)) return false;
        } else {
          if (
            String(value)
              .toLowerCase()
              .indexOf(String(criteriaValue).toLowerCase()) === -1
          )
            return false;
        }
      }

      if (nameTerm) {
        var fullName = (
          record.get("fname") + record.get("lname")
        ).toLowerCase();
        if (fullName.indexOf(nameTerm) === -1) return false;
      }

      return true;
    });

    return filteredRecords.getRange();
  },

  onSearch: function (values) {
    var me = this;
    var playerStore = Ext.getStore("playerstore");

    if (!playerStore) {
      console.error("Không tìm thấy store playerstore");
      return;
    }

    if (!playerStore.isLoaded()) {
      console.log("Store chưa load, đợi xong rồi mới search...");
      playerStore.on(
        "load",
        function () {
          me.onSearch(values); // Gọi lại chính nó
        },
        { single: true }
      );
      return;
    }

    // Xử lý tiêu chí tìm kiếm
    var criteria = {};
    ["id", "nat", "club", "pos", "foot", "rate", "version"].forEach(function (
      key
    ) {
      if (values[key]) {
        criteria[key] = String(values[key]).toLowerCase();
      }
    });

    var nameTerm = values.name ? values.name.toLowerCase() : null;
    var results = me.searchPlayersByCriteria(criteria, nameTerm);

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
    var total = this.getCurrentResults().length;
    var itemsPerPage = this.getItemsPerPage();
    vm.set("hasPrev", this.getCurrentPage() > 1);
    vm.set("hasNext", this.getCurrentPage() * itemsPerPage < total);
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
    else console.warn("Không tìm thấy playerdetails");
  },
});
