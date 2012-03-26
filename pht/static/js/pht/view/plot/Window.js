Ext.define('PHT.view.plot.Window', {
    extend: 'Ext.window.Window',
    alias: 'widget.plotwindow',
    autoScroll: true,
    width: '95%',
    height: '95%',
    //layout: 'border',
    constrainHeader: true,
    title: 'Plots',
    maximizable: true,
    autoshow: true,
    /*
    layout : { type: 'hbox'
             , align: 'stretch'
             },
    items: [{
        xtype : 'lstpressuretotal'
      },{
        xtype: 'lstpressurepoor'
    }],
    */
    layout : { type: 'vbox',
               align: 'stretch',
             },  
    defaults: {
        style: 'margin: 5px 0 0 5px'
    },
         
    items: [{
        layout: { type: 'hbox',
                  align: 'stretch',
                },
        flex: 1,
        defaults: {
            layout: 'fit',
            flex: 1,
        },
        items: [{
            title: 'Total Pressure',
            xtype : 'panel',
            items: [{xtype: 'lstpressuretotal'}],
        },{
            title: 'Poor',
            xtype : 'panel',
            items: [{xtype: 'lstpressurepoor'}],
        }],
      },{
        layout: { type: 'hbox',
                  align: 'stretch',
                },
        flex: 1,
        defaults: {
            layout: 'fit',
            flex: 1,
        },
        items: [{
            title: 'Good',
            xtype : 'panel',
            items: [{xtype: 'lstpressuregood'}],
        },{
            title: 'Excellent',
            xtype : 'panel',
            items: [{xtype: 'lstpressureexcellent'}],
        }],
    }],
    /*             
    items: [{
        layout : { type: 'hbox'
            , align: 'stretch'
                },
        items: [{
            xtype: 'lstpressuretotal',
        }],
      },{  
        layout : { type: 'hbox'
            , align: 'stretch'
                },
        items: [{
            xtype: 'lstpressurepoor',
        }],
    }],
    */

    initComponent: function() {    
        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                {
                    text: 'Update',
                    action: 'update',
                },
            ]
        }];
        this.callParent(arguments);
    },
});


