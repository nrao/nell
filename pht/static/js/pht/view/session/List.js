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
        this.rcvrCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'rcvr',
            store: 'Receivers',
            queryMode: 'local',
            displayField: 'abbreviation',
            valueField: 'abbreviation',
            hideLabel: true,
            emptyText: 'Select a receiver...',
            listeners: {
                select: function(combo, record, index) {
                    var rcvr = record[0].get('abbreviation');
                    grid.setReceiver(rcvr);
                }
            },
        });
    
        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.proposalCombo,
                this.rcvrCombo,
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
            {header: 'Rcvrs', dataIndex: 'receivers', flex: 1},
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
        var rcvr = this.rcvrCombo.getValue();
        this.resetFilter(pcode, rcvr);
        this.proposalCombo.setValue(pcode);
    },

    setReceiver: function(rcvr) {
        var pcode = this.proposalCombo.getValue();
        this.resetFilter(pcode, rcvr);
        this.rcvrCombo.setValue(rcvr);
    },

    // When ever a new filter parameter is applied, we need to
    // clear the filter, but then *reapply* any other appropriate filters
    resetFilter: function(pcode, rcvr) {
        var store = this.getStore('Sessions');
        if (store.isFiltered()){
            store.clearFilter();
        }
        this.filterFor('pcode', pcode);
        this.filterFor('receivers', rcvr);
        store.sync();
    }

    // Need this rather then just store.filter because we want 
    // success if our value is *anywhere* found in field.
    filterFor: function(field, value) {
        if (value != null & value != '') {
            store.filter([{
                filterFn: function(item) {
                    return item.get(field).search(value) > -1;
                }
            }]);    
            
        }    
    }
});
