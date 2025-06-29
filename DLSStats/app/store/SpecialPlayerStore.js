Ext.define('DLSStats.store.SpecialPlayerStore', {
    extend: 'Ext.data.Store',
    alias: 'store.specialplayerstore',

    model: 'DLSStats.model.SpecialPlayer', 

    proxy: {
        type: 'ajax',
        url: 'resources/data/special.json',
        reader: {
            type: 'json',
            rootProperty: '' 
        }
    },

    autoLoad: true
});


