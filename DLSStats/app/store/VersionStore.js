Ext.define('DLSStats.store.VersionStore', {
    extend: 'Ext.data.Store',
    alias: 'store.versionstore',
    storeId: 'versionstore',

    fields: ['version'],

    data: [
        { version: '20263' },
        { version: '20262' },
        { version: '20261' },
        { version: '20253' },
        { version: '20252' },
        { version: '20251' },
        { version: '20242' },
        { version: '20241' },
        { version: '20231' }
    ]
});