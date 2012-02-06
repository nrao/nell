Ext.define('PHT.view.session.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.sessionlist',
    store : 'Sessions', 


    initComponent: function() {
        var grid = this;
        this.proposalCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'pcode',
            store: 'ProposalCodes',
            queryMode: 'local',
            displayField: 'pcode',
            valueField: 'pcode',
            hideLabel: true,
            emptyText: 'Select a proposal...',
            listeners: {
                select: function(combo, record, index) {
                    var pcode = record[0].get('pcode');
                    grid.setProposal(pcode);
                }
            },
        });
    
        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.proposalCombo,
                Ext.create('Ext.button.Button', {
                    text: 'Clear Filters',
                    action: 'clear',
                }),
                { xtype: 'tbseparator' },
                Ext.create('Ext.button.Button', {
                    text: 'Create Session',
                    action: 'create',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Delete Session',
                    action: 'delete',
                }),
            ]},
        ];

        this.columns = [
            {header: 'PCODE', dataIndex: 'pcode', width: 100},
            {header: 'Name', dataIndex: 'name', width: 100},
            {header: 'Requested', dataIndex: 'requested_time', flex: 1},
            {header: 'Repeats', dataIndex: 'repeats', flex: 1},
            {header: 'Separation', dataIndex: 'separation', flex: 1},
            {header: 'Interval', dataIndex: 'interval_time', flex: 1},
            {header: 'Constraint', dataIndex: 'constraint_field', flex: 1},
            {header: 'Comments', dataIndex: 'comments', flex: 1},
            {header: 'Min LST', dataIndex: 'min_lst', flex: 1},
            {header: 'Max LST', dataIndex: 'max_lst', flex: 1},
            {header: 'El Min', dataIndex: 'elevation_min', flex: 1},
            {header: 'Sess Time Calc', dataIndex: 'session_time_calculated', flex: 1},
        ];

        this.callParent(arguments);
    },

    setProposal: function(pcode) {
        var store = this.getStore('Sessions');
        if (store.isFiltered()){
            store.clearFilter();
        }
        store.filter("pcode", pcode);
        this.proposalCombo.setValue(pcode);
        store.sync();
    },
});
