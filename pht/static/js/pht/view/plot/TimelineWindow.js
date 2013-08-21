Ext.define('PHT.view.plot.TimelineWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.timelineplotwindow',
    autoScroll: true,
    title: 'Timeline Plot',
    constrain: true,
    layout: 'fit',
    width: '95%',
    height: '95%',
    plain: true,
    maximizable: true,
    /*
    x: 0,
    y: 0,
    items: {
        border: false
    },
    */

    /*
    width: '95%',
    height: '95%',
    constrainHeader: true,
    title: 'Timeline Plot',
    maximizable: true,
    autoshow: true,
    layout : { type: 'vbox',
               align: 'stretch',
             },  
    defaults: {
        style: 'margin: 5px 0 0 5px'
    },
    */     
    initComponent: function() {

        this.proposalCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'pcode',
            store: 'Proposals',
            queryMode: 'local',
            displayField: 'pcode',
            valueField: 'pcode',
            hideLabel: false,
            fieldLabel: 'Proposal',
            emptyText: 'Select a proposal...',
        });

        this.sponsorCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'abbreviation',
            store: 'Partners',
            queryMode: 'local',
            displayField: 'abbreviation',
            valueField: 'abbreviation',
            hideLabel: false,
            fieldLabel: 'Sponsor',
            emptyText: 'Select a sponsor...',
            value: 'WVU',
        });

        this.timeCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'semester',
            store: 'Semesters',
            queryMode: 'local',
            displayField: 'semester',
            valueField: 'semester',
            hideLabel: false,
            fieldLabel: 'Time Range',
            emptyText: 'Select a time range...',
        });

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
              {
                text: 'Update',
                action: 'update'
              },
              {
                xtype: 'tbseparator'
              },
              this.proposalCombo,
              this.sponsorCombo,
              {
                xtype: 'tbseparator'
              },
              this.timeCombo,
            ],
        }];        
        this.items =[
            { 
              xtype: 'timelineplot'
            },
        ];

        this.callParent(arguments);        
    },

    close: function() {
        this.hide();
    },

});
        
