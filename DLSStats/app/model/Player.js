Ext.define("DLSStats.model.Player", {
  extend: "Ext.data.Model",
  idProperty: "uid",

  fields: [
    "fname",
    "lname",
    "nat",
    "club",
    "pos",
    "foot",
    "rate",
    "hgt",
    "spe",
    "acc",
    "sta",
    "str",
    "con",
    "pas",
    "sho",
    "tac",
    "prc",
    "id",
    "version",
    {
      name: "uid",
      calculate: function (data) {
        return data.id + "_" + data.version;
      },
    },
  ],
});
