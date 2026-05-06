Ext.define("DLSStats.store.PlayerStore", {
    extend: "Ext.data.Store",
    alias: "store.playerstore",
    storeId: "playerstore",

    model: "DLSStats.model.Player",

    // Không dùng proxy/autoLoad — load thủ công từng file version
    autoLoad: false,

    // Danh sách version cần load (khớp với VersionStore)
    versions: ["20231", "20241", "20242", "20251", "20252", "20253", "20261", "20262"],

    constructor: function (config) {
        this.callParent([config]);
        this._loadAllVersions();
    },

    _loadAllVersions: function () {
        var me = this;
        var versions = me.versions;
        var allRecords = [];
        var remaining = versions.length;

        if (remaining === 0) {
            me.loadData([]);
            me.fireEvent("load", me, [], true);
            return;
        }

        versions.forEach(function (ver) {
            Ext.Ajax.request({
                url: "resources/data/" + ver + ".json",
                success: function (response) {
                    try {
                        var data = Ext.decode(response.responseText);
                        if (Ext.isArray(data)) {
                            // Thêm (old) vào lname nếu status = 0
                            data.forEach(function (rec) {
                                if (rec.status === 0 && rec.lname &&
                                    rec.lname.indexOf("(old)") === -1) {
                                    rec.lname = rec.lname + " (old)";
                                }
                            });
                            allRecords = allRecords.concat(data);
                        }
                    } catch (e) {
                        console.error("Failed to parse " + ver + ".json", e);
                    }
                },
                failure: function () {
                    console.warn("Could not load resources/data/" + ver + ".json");
                },
                callback: function () {
                    remaining--;
                    if (remaining === 0) {
                        me.loadData(allRecords);
                        me.fireEvent("load", me, me.getRange(), true);
                    }
                }
            });
        });
    }
});
