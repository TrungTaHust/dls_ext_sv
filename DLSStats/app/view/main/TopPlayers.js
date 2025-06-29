Ext.define('DLSStats.view.main.TopPlayers', {
    extend: 'Ext.container.Container',
    xtype: 'dls-topplayers',

    layout: 'fit',
    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
    },

    items: [
        {
            xtype: 'tabpanel',
            tabBar: {
                defaults: {
                    style: {
                        'writing-mode': 'horizontal-tb',
                        'text-align': 'left',
                        'padding-left': '10px'
                    }
                }
            },
            activeTab: 0,
            defaults: {
                width: 600,
                padding: 10,
                layout: 'vbox'
            },
            items: [
                {
                    title: 'Top 5 on POSITION',
                    items: [
                        {
                            xtype: 'segmentedbutton',
                            reference: 'positionSelector',
                            items: [
                                { text: 'CF', pressed: true },
                                { text: 'LW' },
                                { text: 'RW' },
                                { text: 'SS' },
                                { text: 'CM' },
                                { text: 'AM' },
                                { text: 'DM' },
                                { text: 'LM' },
                                { text: 'RM' },
                                { text: 'LWB' },
                                { text: 'RWB' },
                                { text: 'CB' },
                                { text: 'LB' },
                                { text: 'RB' },
                                { text: 'GK' },
                            ],
                            listeners: {
                                toggle: function (container, button, pressed) {
                                    if (pressed) {
                                        let grid = container.up('panel').down('grid[reference=topByPosition]');
                                        grid.getStore().filter('position', button.getText());
                                    }
                                }
                            }
                        },
                        {
                            xtype: 'grid',
                            reference: 'topByPosition',
                            columns: [
                                { text: 'Name', dataIndex: 'full_name', width: 400 },
                                { text: 'Position', dataIndex: 'position', width: 100 },
                                { text: 'Rating', dataIndex: 'rating', width: 100 }
                            ]
                        }
                    ]
                },
                {
                    title: 'Top 5 on STATS',
                    items: [
                        {
                            xtype: 'segmentedbutton',
                            reference: 'statsSelector',
                            items: [
                                { text: 'SPE', pressed: true },
                                { text: 'ACC' },
                                { text: 'STA' },
                                { text: 'STR' },
                                { text: 'CON' },
                                { text: 'PAS' },
                                { text: 'SHO' },
                                { text: 'TAC' }
                            ],
                            listeners: {
                                toggle: function (container, button, pressed) {
                                    if (pressed) {
                                        let grid = container.up('panel').down('grid[reference=topByStats]');
                                        let store = grid.getStore();
                                        let statField = button.getText().toLowerCase();

                                        store.sort({ property: statField, direction: 'DESC' });

                                        let statCol = grid.columns[2];
                                        statCol.setText(button.getText());
                                        statCol.dataIndex = statField;

                                        grid.getView().refresh();
                                    }
                                }

                            }
                        },
                        {
                            xtype: 'grid',
                            reference: 'topByStats',
                            flex: 1,
                            columns: [
                                { text: 'Name', dataIndex: 'full_name', width: 400 },
                                { text: 'Rating', dataIndex: 'rating', width: 100 },
                                { text: 'SPE', dataIndex: 'spe', width: 100 }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
});
