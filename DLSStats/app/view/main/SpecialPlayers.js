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
        'DLSStats.view.main.PlayerController',
        'DLSStats.store.SpecialPlayerStore',
        'DLSStats.model.SpecialPlayer'
    ],

    controller: 'player',
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
                                return rec.get('first_name') + ' ' + rec.get('last_name');
                            }
                        },
                        {
                            text: 'Position',
                            dataIndex: 'position',
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
                                meta.style = 'color: ' + color + '; font-weight: bold; text-align: center';
                                return value ? value.toUpperCase() : '';
                            }
                        },
                        {
                            text: 'Rating',
                            dataIndex: 'rating',
                            align: 'center',
                            flex: 1,
                            minWidth: 80,
                            sortable: false,
                            menuDisabled: true,
                            renderer: function (v, meta, rec) {
                                meta.style = 'font-weight: bold';
                                return rec.get('rating');
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
                minWidth: 280,
                maxWidth: 400,
                responsiveConfig: {
                    'width < 600': { maxWidth: null }
                },
                reference: 'playerdetails',
                title: 'Player Details',
                scrollable: true,
                bodyPadding: 10,
                referenceHolder: true,

                layout: {
                    type: 'vbox',
                    align: 'stretch',
                    //width: 600,
                },

                items: [
                    // Header
                    {
                        xtype: 'container',
                        reference: 'headerContainer',
                        style: {
                            backgroundColor: '#f0f0f0'
                        },
                        items: [{
                            xtype: 'component',
                            reference: 'name',
                            html: '<h2 style="text-align:center;">No player selected</h2>',
                        }]
                    },
                    // Basic info
                    {
                        xtype: 'container',
                        reference: 'basicInfoContainer',
                        layout: {
                            type: 'hbox',
                            align: 'stretch'
                        },
                        responsiveConfig: {
                            'width < 600': {
                                layout: {
                                    type: 'vbox',
                                    align: 'stretch'
                                }
                            }
                        },

                        defaults: {
                            xtype: 'container',
                            layout: 'vbox',
                            flex: 1,
                            padding: '0 10',
                            defaults: {
                                xtype: 'component',
                                margin: '8 0'
                            }
                        },

                        items: [
                            {
                                items: [
                                    { reference: 'type', html: 'Type: ' },
                                    { reference: 'nationality', html: 'Nationality: ' },
                                    { reference: 'position', html: 'Position: ' },
                                    { reference: 'version', html: 'Version: ' },
                                ]
                            },
                            {
                                items: [
                                    { reference: 'foot', html: 'Leg: ' },
                                    { reference: 'rating', html: 'Rating: ' },
                                    { reference: 'height', html: 'Height: ' }
                                ]
                            }
                        ]
                    },
                    // Stats
                    {
                        xtype: 'container',
                        reference: 'statsContainer',
                        layout: {
                            type: 'vbox',
                            align: 'center'
                        },
                        margin: '10 0',

                        defaults: {
                            width: '100%',
                            //maxWidth: 500,
                            margin: '5 0'
                        },

                        items: [
                            {
                                xtype: 'container',
                                layout: {
                                    type: 'hbox',
                                    align: 'stretch'
                                },
                                responsiveConfig: {
                                    'width < 600': {
                                        layout: {
                                            type: 'vbox',
                                            align: 'stretch'
                                        }
                                    }
                                },
                                defaults: {
                                    xtype: 'component',
                                    flex: 1,
                                    padding: 5,
                                    margin: 5,
                                    style: 'text-align:center; border: 1px solid #ccc; font-weight: bold;'
                                },
                                items: [
                                    { reference: 'speed', html: 'SPE: ?' },
                                    { reference: 'acceleration', html: 'ACC: ?' },
                                    { reference: 'stamina', html: 'STA: ?' },
                                    { reference: 'strength', html: 'STR: ?' }
                                ],
                            },
                            {
                                xtype: 'container',
                                layout: {
                                    type: 'hbox',
                                    align: 'stretch'
                                },
                                responsiveConfig: {
                                    'width < 600': {
                                        layout: {
                                            type: 'vbox',
                                            align: 'stretch'
                                        }
                                    }
                                },
                                defaults: {
                                    xtype: 'component',
                                    flex: 1,
                                    padding: 5,
                                    margin: 5,
                                    style: 'text-align:center; border: 1px solid #ccc; font-weight: bold;'
                                },
                                items: [
                                    { reference: 'control', html: 'CON: ?' },
                                    { reference: 'passing', html: 'PAS: ?' },
                                    { reference: 'shooting', html: 'SHO: ?' },
                                    { reference: 'tackling', html: 'TAC: ?' }
                                ],
                            }
                        ]
                    }
                ],

                updatePlayer: function (player) {
                    if (!player || !player.last_name) {
                        this.lookupReference('name').setHtml('<h2>No player selected</h2>');
                        return;
                    }

                    function getStatColor(val) {
                        val = parseInt(val, 10);
                        if (isNaN(val)) return 'lightgray';
                        if (val >= 90) return 'cyan';
                        if (val >= 80) return 'lime';
                        if (val >= 70) return 'yellow';
                        if (val >= 60) return 'orange';
                        if (val >= 50) return 'crimson';
                        return 'red';
                    }

                    var me = this;

                    function setStatsColor(ref, val, prefix) {
                        var cmp = me.lookupReference(ref);
                        if (cmp) {
                            cmp.setHtml(prefix + (val != null ? val : '?'));
                            var color = getStatColor(val);
                            cmp.setStyle({
                                'background-color': 'black',
                                'color': color
                            });
                        }
                    }

                    function set(ref, val, prefix) {
                        var cmp = me.lookupReference(ref);
                        if (cmp) {
                            cmp.setHtml('<b>' + prefix + (val != null ? val : '?') + '</b>');
                        }
                    }

                    // Header
                    var rating = parseInt(player.rating, 10);
                    var bgColor = 'grey';
                    if (rating >= 80) bgColor = 'gold';
                    else if (rating >= 70) bgColor = 'aqua';

                    var headerContainer = this.lookupReference('headerContainer');
                    if (headerContainer) {
                        headerContainer.setStyle('background-color', bgColor);
                    }

                    this.lookupReference('name').setHtml('<h2>' + player.first_name + ' ' + player.last_name + '</h2>');

                    // Basic Info
                    set('type', player.type, 'Type: ');
                    set('nationality', player.nationality, 'Nationality: ');
                    set('position', player.position, 'Position: ');
                    set('foot', player.foot, 'Leg: ');
                    set('rating', player.rating, 'Rating: ');
                    set('height', player.height, 'Height: ');
                    set('version', player.version, 'Version: ');

                    // Stats
                    setStatsColor('speed', player.speed, 'SPE: ');
                    setStatsColor('acceleration', player.acceleration, 'ACC: ');
                    setStatsColor('stamina', player.stamina, (player.position === 'GK' ? 'GKR: ' : 'STA: '));
                    setStatsColor('strength', player.strength, 'STR: ');
                    setStatsColor('control', player.control, 'CON: ');
                    setStatsColor('passing', player.passing, 'PAS: ');
                    setStatsColor('shooting', player.shooting, (player.position === 'GK' ? 'GKH: ' : 'SHO: '));
                    setStatsColor('tackling', player.tackling, 'TAC: ');
                }
            }
        ]
    }]
});
