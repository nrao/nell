Ext.define('PHT.view.dashboard.ImportReports', {
    extend: 'Ext.form.Panel',
    alias : 'widget.importreports',
    title : 'Reports from Imports',

    initComponent: function() {

        this.reportDates = Ext.create('Ext.form.field.ComboBox', {
               name: 'create_date',
               fieldLabel: 'Report Date',
               store : 'ImportReports',
               queryMode: 'local',
               displayField: 'create_date',
               valueField: 'create_date',
               emptyText: 'Select date report was created...',
               listeners: {
                   scope: this,
                   select: function(combo, record, index) {
                       var r = record[0].get('report');
                       this.reportText.setValue(r);
                    }
                },   
        });
 
        this.reportText =  Ext.create('Ext.form.field.TextArea', {
               name: 'report',
               fieldLabel: 'Report',
               width: 600,
               height: 300,
               readOnly: true,
        });

        this.items = [
            this.reportDates,
            this.reportText,
        ],
        this.callParent(arguments);
    },
});    

