Ext.application({
    extend: 'DLSStats.Application',
    name: 'DLSStats',
    requires: [
        'DLSStats.*'
    ],
    
    stores: [
        'PlayerStore'
    ],
    mainView: 'DLSStats.view.main.Main'
});
