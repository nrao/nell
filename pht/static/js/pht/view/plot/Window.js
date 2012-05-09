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
            store: 'Proposals',
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
        var plotTypes = Ext.create('Ext.data.Store', {
            fields: ['type'],
            data:[
                {'type' : 'Total'},
                {'type' : 'Poor'},
                {'type' : 'Good'},
                {'type' : 'Excellent'},
                ]
        });
         this.plotTypesCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'plotType',
            store: plotTypes,
            queryMode: 'local',
            //lastQuery: '',
            displayField: 'type',
            valueField: 'type',
            hideLabel: true,
            emptyText: 'Select a plot type...',
        });
        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                {
                    text: 'Update',
                    action: 'update',
                }
                ,{
                    xtype: 'tbseparator'
                },
                this.proposalCombo,
                this.sessionCombo,
                Ext.create('Ext.button.Button', {
                        text: 'Clear Filters',
                        action: 'clear',
                }),
                {
                    xtype: 'tbseparator'
                },
                this.plotTypesCombo,
                {
                    text: 'Print',
                    action: 'print',
                },
            ]
        }];

        this.items = [{
            xtype: 'tabpanel',
            //layout: 'fit',
            items: [{
              title: 'All',
              bodyPadding: 10,
              layout: {type: 'table',
                       columns: 2,
                       },
              defaults: {
                  bodyStyle: 'padding:20px', 
              },
              items: [{
                  title: 'Total Pressure',
                  xtype : 'panel',
                  layout: 'fit',
                  flex: 1,
                  items: [Ext.create('PHT.view.plot.LstPressureTotal', {width: 500, height: 300})]
              },
              {
                  title: 'Poor',
                  xtype : 'panel',
                  layout: 'fit',
                  flex: 1,
                  items: [Ext.create('PHT.view.plot.LstPressurePoor', {width: 500, height: 300})]
              },
              {
                  title: 'Good',
                  xtype : 'panel',
                  layout: 'fit',
                  flex: 1,
                  items: [Ext.create('PHT.view.plot.LstPressureGood', {width: 500, height: 300})]
              },{
                  title: 'Excellent',
                  xtype : 'panel',
                  layout: 'fit',
                  flex: 1,
                  items: [Ext.create('PHT.view.plot.LstPressureExcellent', {width: 500, height: 300})]
              }],
                },
            {
              title: 'Total',
              bodyPadding: 10,
              height: 800,
              layout: 'fit',
              items: [{
                layout: 'fit',
                flex: 1,
                title: 'Total Pressure',
                xtype : 'panel',
                items: [{xtype: 'lstpressuretotal'}],
                }]
            },
            {
              title: 'Poor',
              height: 800,
              bodyPadding: 10,
              layout: 'fit',
              items: [{
                layout: 'fit',
                flex: 1,
                title: 'Poor',
                xtype : 'panel',
                items: [{xtype: 'lstpressurepoor'}],
                }]
            },
            {
              title: 'Good',
              height: 800,
              bodyPadding: 10,
              layout: 'fit',
              items: [{
                layout: 'fit',
                flex: 1,
                title: 'Good',
                xtype : 'panel',
                items: [{xtype: 'lstpressuregood'}],
                }]
            },
            {
              title: 'Excellent',
              height: 800,
              bodyPadding: 10,
              layout: 'fit',
              items: [{
                layout: 'fit',
                flex: 1,
                title: 'Excellent',
                xtype : 'panel',
                items: [{xtype: 'lstpressureexcellent'}],
                }]
            },
            ]
        }];

        this.callParent(arguments);
    },        

    initLayout: function() {
        // display the 4 plots in a 2 x 2 table
        return [{
            layout: { type: 'hbox',
                      align: 'stretch',
                    },
            flex: 1,
            defaults: {
                layout: 'fit',
                flex: 1,
            },
            items: [
                {
                    title: 'Total Pressure',
                    xtype : 'panel',
                    items: [{xtype: 'lstpressuretotal'}],
                },
                {
                    title: 'Poor',
                    xtype : 'panel',
                    items: [{xtype: 'lstpressurepoor'}],
                },
                ],
          }
          ,{
            layout: { type: 'hbox',
                      align: 'stretch',
                    },
            flex: 1,
            defaults: {
                layout: 'fit',
                flex: 1,
            },
            items: [
                {
                    title: 'Good',
                    xtype : 'panel',
                    items: [{xtype: 'lstpressuregood'}],
                },{
                    title: 'Excellent',
                    xtype : 'panel',
                    items: [{xtype: 'lstpressureexcellent'}],
                }],
        }];

    },

    close: function() {
        this.hide();
    }
});


