Ext.define('PHT.view.plot.Window', {
    extend: 'Ext.window.Window',
    alias: 'widget.plotwindow',
    autoScroll: true,
    width: '95%',
    height: '95%',
    constrainHeader: true,
    title: 'Plots',
    maximizable: true,
    autoshow: true,
    layout : { type: 'vbox',
               align: 'stretch',
             },  
    defaults: {
        style: 'margin: 5px 0 0 5px'
    },
         
    initComponent: function() {

        this.proposalCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'pcode',
            store: 'ProposalCodes',
            queryMode: 'local',
            displayField: 'pcode',
            valueField: 'pcode',
            hideLabel: true,
            emptyText: 'Select a proposal...',
        });
         this.sessionCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'session',
            store: 'Sessions',
            queryMode: 'local',
            lastQuery: '',
            displayField: 'name',
            valueField: 'id',
            hideLabel: true,
            emptyText: 'Select a session...',
        });

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                {
                    text: 'Update',
                    action: 'update',
                },{
                    xtype: 'tbseparator'
                },
                this.proposalCombo,
                this.sessionCombo,
                Ext.create('Ext.button.Button', {
                        text: 'Clear Filters',
                        action: 'clear',
                }),
            ]
        }];
        this.callParent(arguments);
    },        

    // display the 4 plots in a 2 x 2 table
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
});


