Ext.define('DLSStats.view.main.SpecialPlayers', {
    extend: 'Ext.container.Container',
    xtype: 'dls-specialplayers',
    layout: 'fit',
    scrollable: true,

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
    },

    requires: [
        'DLSStats.view.main.PlayerDetails',
        'DLSStats.view.main.SpecialPlayersController',
        'DLSStats.store.SpecialPlayerStore',
        'DLSStats.model.SpecialPlayer'
    ],

    controller: 'specialplayers',
    referenceHolder: true,

    viewModel: {
        data: {
            hasPrev: false,
            hasNext: false
        },
        stores: {
            specialplayers: {
                type: 'specialplayerstore'
            }
        }
    },

    items: [{
        xtype: 'container',
        reference: 'responsiveContent',
        layout: {
            type: 'hbox',
            pack: 'center'
        },
        responsiveConfig: {
            'width < 600': {
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                }
            },
            'width >= 600': {
                layout: {
                    type: 'hbox',
                    pack: 'center'
                }
            }
        },
        defaults: {
            margin: 20,
            flex: 1
        },
        items: [
            {
                xtype: 'panel',
                layout: 'fit',
                bodyPadding: 5,
                title: 'Player List',
                responsiveConfig: {
                    'width < 600': { maxWidth: null },
                    'width >= 600': { maxWidth: 520 }
                },
                minWidth: 300,
                maxWidth: 520,
                items: [{
                    xtype: 'grid',
                    height: 400,
                    width: 600,
                    reference: 'playerList',
                    bind: { store: '{specialplayers}' },
                    columnLines: true,
                    rowLines: true,
                    scrollable: true,
                    columns: [
                        {
                            text: 'Name',
                            flex: 2,
                            minWidth: 150,
                            sortable: false,
                            menuDisabled: true,
                            renderer: function (v, meta, rec) {
                                meta.style = 'font-weight: bold';
                                return rec.get('fname') + ' ' + rec.get('lname');
                            }
                        },
                        {
                            text: 'Position',
                            dataIndex: 'pos',
                            align: 'center',
                            flex: 1,
                            minWidth: 80,
                            sortable: false,
                            menuDisabled: true,
                            renderer: function (value, meta) {
                                var pos = (value || '').toLowerCase();
                                var bgColor = 'black';
                                var color = 'black';

                                if (['cf', 'ss', 'lw', 'rw'].indexOf(pos) >= 0) {
                                    bgColor = 'red';
                                } else if (['cm', 'am', 'dm', 'lm', 'rm', 'lwb', 'rwb'].indexOf(pos) >= 0) {
                                    bgColor = 'yellow';
                                } else if (['cb', 'lb', 'rb'].indexOf(pos) >= 0) {
                                    bgColor = 'lime';
                                } else if (pos === 'gk') {
                                    bgColor = 'cyan';
                                }

                                meta.style = 'background-color: ' + bgColor + '; color: ' + color + '; font-weight: bold; text-align: center';
                                return value ? value.toUpperCase() : '';
                            }
                        },
                        {
                            text: 'Type',
                            dataIndex: 'type',
                            align: 'center',
                            flex: 1,
                            minWidth: 80,
                            sortable: false,
                            menuDisabled: true,
                            renderer: function (value, meta) {
                                var pos = (value || '').toLowerCase();
                                var color = 'white';

                                if (pos === 'classic') {
                                    color = 'black';
                                } else if (pos === 'star') {
                                    color = 'purple';
                                } else if (pos === 'champion') {
                                    color = 'blue';
                                }
                                else if (pos === 'team') {
                                    color = 'green';
                                }
                                meta.style = 'color: ' + color + '; font-weight: bold; text-align: center';
                                return value ? value.toUpperCase() : '';
                            }
                        },
                        {
                            text: 'Rating',
                            dataIndex: 'rate',
                            align: 'center',
                            flex: 1,
                            minWidth: 80,
                            sortable: false,
                            menuDisabled: true,
                            renderer: function (v, meta, rec) {
                                meta.style = 'font-weight: bold';
                                return rec.get('rate');
                            }
                        }
                    ],
                    listeners: {
                        itemclick: 'onPlayerSelect'
                    }
                }]
            },
            // Player Detail
            {
                xtype: 'dls-playerdetails',
                reference: 'playerdetails',
                minWidth: 280,
                maxWidth: 400,
                responsiveConfig: {
                    'width < 600': { maxWidth: null }
                }
            }
        ]
    }]
});