Ext.define('PHT.view.plot.Window', {
    extend: 'Ext.window.Window',
    alias: 'widget.plotwindow',
    autoScroll: true,
    width: '90%',
    height: '90%',
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
        style: 'margin: 10px 0 0 10px'
    },
         
    items: [{
        layout: { type: 'hbox',
                  align: 'stretch',
                },
        flex: 1,
        items: [{
            title: 'Total',
            xtype : 'lstpressuretotal',
            flex: 1,
        },{
            title: 'Poor',
            xtype : 'lstpressurepoor',
            flex: 1,
        }],
      },{
        layout: { type: 'hbox',
                  align: 'stretch',
                },
        flex: 1,
        items: [{
            title: 'Good',
            xtype : 'lstpressuregood',
            flex: 1,
        },{
            title: 'Excellent',
            xtype : 'lstpressureexcellent',
            flex: 1,
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


