Ext.define('DLSStats.view.main.Temp', {
    extend: 'Ext.container.Container',
    xtype: 'dls-temp',
    title: 'Compare Players',

    style: {
        backgroundImage: 'url("./app/res/background.jpg")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
    },

    requires: [
        'DLSStats.view.main.PlayerController',
    ],

    controller: 'player',
    referenceHolder: true,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    padding: 10,

    items: [
        {
            xtype: 'container',
            layout: {
                type: 'hbox',
                pack: 'center',
                align: 'middle'
            },
            defaults: {
                xtype: 'textfield',
                margin: 20,
                width: 200
            },
            items: [
                {
                    itemId: 'player1Id',
                    emptyText: 'Enter Player 1 ID'
                },
                {
                    itemId: 'player2Id',
                    emptyText: 'Enter Player 2 ID'
                }
            ]
        },
        {
            xtype: 'container',
            layout: {
                type: 'hbox',
                pack: 'center',
                align: 'middle'
            },
            margin: 10,
            items: [
                {
                    xtype: 'button',
                    text: 'Compare',
                    width: 120,
                    style: {
                        backgroundColor: 'green',
                        color: 'black'
                    },                    
                }
            ]
        }
        ,
        {
            xtype: 'container',
            layout: {
                type: 'vbox',
                pack: 'center',
                align: 'center'
            },
            defaults: {
                xtype: 'panel',
                width: 610,
                scrollable: true,
                style: {
                    border: '1px solid #ccc',
                    backgroundColor: '#fafafa'
                }
            },
            items: [
                {
                    xtype: 'container',
                    layout: {
                        type: 'hbox',
                        pack: 'center',
                        align: 'center'
                    },
                    defaults: {
                        xtype: 'panel',
                        width: 300,
                        scrollable: true,
                        style: {
                            border: '1px solid #ccc',
                            backgroundColor: '#fafafa'
                        }
                    },
                    items: [
                        {
                            title: 'P1',
                        },
                        {
                            title: 'P2',
                        }
                    ]
                },
                {
                    xtype: 'container',
                    layout: {
                        type: 'hbox',
                        pack: 'center',
                        align: 'center'
                    },
                    defaults: {
                        xtype: 'panel',
                        width: 200,
                        scrollable: true,
                        style: {
                            border: '1px solid #ccc',
                            backgroundColor: '#fafafa'
                        }
                    },
                    items: [
                        {
                            xtype: 'container',
                            layout: 'vbox',
                            defaults: {
                                xtype: 'component',
                                flex: 1,
                                padding: 5,
                                margin: 5,
                                style: 'text-align:center; border: 1px solid #ccc; font-weight: bold;'
                            },
                            items: [
                                { reference: 'speed1', html: 'SPE: ?' },
                                { reference: 'acceleration1', html: 'ACC: ?' },
                                { reference: 'stamina1', html: 'STA: ?' },
                                { reference: 'strength1', html: 'STR: ?' },
                                { reference: 'control1', html: 'CON: ?' },
                                { reference: 'passing1', html: 'PAS: ?' },
                                { reference: 'shooting1', html: 'SHO: ?' },
                                { reference: 'tackling1', html: 'TAC: ?' },
                                { reference: 'ovr1', html: 'OVR: ?' },
                            ]
                        }, {
                            xtype: 'panel',
                            width: 100,
                            layout: {
                                type: 'vbox',
                                align: 'center'
                            },
                            itemId: 'compareColumn',
                            defaults: {
                                xtype: 'component',
                                flex: 1,
                                padding: 5,
                                margin: 5,
                                style: 'text-align: center; font-weight: bold; font-size: 18px; margin: 5px;'
                            },
                            items: [
                                { itemId: 'cmp_speed', html: '?' },
                                { itemId: 'cmp_acceleration', html: '?' },
                                { itemId: 'cmp_stamina', html: '?' },
                                { itemId: 'cmp_strength', html: '?' },
                                { itemId: 'cmp_control', html: '?' },
                                { itemId: 'cmp_passing', html: '?' },
                                { itemId: 'cmp_shooting', html: '?' },
                                { itemId: 'cmp_tackling', html: '?' },
                                { itemId: 'cmp_ovr', html: '?' }
                            ]
                        },
                        {
                            xtype: 'container',
                            layout: 'vbox',
                            defaults: {
                                xtype: 'component',
                                flex: 1,
                                padding: 5,
                                margin: 5,
                                style: 'text-align:center; border: 1px solid #ccc; font-weight: bold;'
                            },
                            items: [
                                { reference: 'speed2', html: 'SPE: ?' },
                                { reference: 'acceleration2', html: 'ACC: ?' },
                                { reference: 'stamina2', html: 'STA: ?' },
                                { reference: 'strength2', html: 'STR: ?' },
                                { reference: 'control2', html: 'CON: ?' },
                                { reference: 'passing2', html: 'PAS: ?' },
                                { reference: 'shooting2', html: 'SHO: ?' },
                                { reference: 'tackling2', html: 'TAC: ?' },
                                { reference: 'ovr2', html: 'OVR: ?' },
                            ]
                        }
                    ]
                },
            ]
        }
    ]
});
