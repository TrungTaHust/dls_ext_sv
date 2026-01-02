Ext.define("DLSStats.store.PlayerStore", {
  extend: "Ext.data.Store",
  alias: "store.playerstore",
  storeId: "playerstore",

  model: "DLSStats.model.Player",

  proxy: {
    type: "ajax",
    url: "resources/data/data.json",
    reader: {
      type: "json",
      rootProperty: "",
    },
  },

  autoLoad: true,
});
