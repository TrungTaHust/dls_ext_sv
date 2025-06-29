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
    if (form) {
      form.on("searchrequest", this.onSearch, this);
    }
  },

  onSearch: function (values) {
    var me = this;
    var criteria = {};
    ["id", "nat", "club", "pos", "foot", "rate", "version"].forEach(function (
      key
    ) {
      if (values[key]) {
        criteria[key] = values[key].toLowerCase();
      }
    });

    if (!criteria.id) {
      delete criteria.id;
    }

    console.log("Sending request to API...");

    fetch("https://trungta-hust-dls24.vercel.app/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nameTerm: values.name ? values.name.toLowerCase() : "",
        criteria: criteria,
      }),
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        me.setCurrentResults(data);
        me.setCurrentPage(1);
        me.updatePaging();
        me.loadPage(1);
      })
      .catch(function (err) {
        Ext.Msg.alert("Error", "Lỗi khi gọi API");
        console.error(err);
      });
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
    if (detailPanel) {
      detailPanel.updatePlayer(player);
    } else {
      console.warn("Không tìm thấy playerdetails");
    }
  },
});
