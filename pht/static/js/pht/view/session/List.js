Ext.define('PHT.view.session.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.sessionlist',
    store : 'Sessions', 
    multiSelect: true,

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
        this.sciCatCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'category',
            store: 'ScienceCategories',
            queryMode: 'local',
            displayField: 'category',
            valueField: 'id',
            hideLabel: true,
            emptyText: 'Select a category...',
            listeners: {
                select: function(combo, record, index) {
                    var cat = record[0].get('category');
                    grid.setScienceCategory(cat);
                }
            },
        });
    
        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.proposalCombo,
                this.rcvrCombo,
                this.sciCatCombo,
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
                    text: 'Edit Session(s)',
                    action: 'edit',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Delete Session',
                    action: 'delete',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Duplicate Session',
                    action: 'duplicate',
                }),
            ]},
        /*
        TBF: Hold for paging
        {
            xtype: 'pagingtoolbar',
            store: 'Sessions',
            dock: 'bottom',
            displayInfo: true
        }
        */
        ];

        this.columns = [
            {header: 'PCODE', dataIndex: 'pcode', width: 100},
            {header: 'Name', dataIndex: 'name', width: 100},
            {header: 'Type', dataIndex: 'session_type_code', flex: 1},
            {header: 'Obs. Type', dataIndex: 'observing_type', width: 80},
            {header: 'Requested', dataIndex: 'requested_time', flex: 1},
            {header: 'Repeats', dataIndex: 'repeats', flex: 1},
            {header: 'Separation', dataIndex: 'separation', flex: 1},
            {header: 'Rcvrs', dataIndex: 'receivers', flex: 1},
            {header: 'Backends', dataIndex: 'backends', width: 100},
            {header: 'Interval', dataIndex: 'interval_time', flex: 1},
            {header: 'Constraint?', dataIndex: 'has_constraint_field', flex: 1},
            {header: 'Comments?', dataIndex: 'has_comments', flex: 1},
            {header: 'Min LST', dataIndex: 'min_lst', width: 100},
            {header: 'Max LST', dataIndex: 'max_lst', width: 100},
            {header: 'El Min', dataIndex: 'elevation_min', flex: 1},
        ];

        this.callParent(arguments);
    },

    setProposal: function(pcode) {
        var rcvr = this.rcvrCombo.getValue();
        var cat  = this.sciCatCombo.getValue();
        this.resetFilter(pcode, rcvr, cat);
        this.proposalCombo.setValue(pcode);
    },

    setReceiver: function(rcvr) {
        var pcode = this.proposalCombo.getValue();
        var cat   = this.sciCatCombo.getValue();
        this.resetFilter(pcode, rcvr, cat);
        this.rcvrCombo.setValue(rcvr);
    },

    setScienceCategory: function(cat) {
        var pcode = this.proposalCombo.getValue();
        var rcvr  = this.rcvrCombo.getValue();
        this.resetFilter(pcode, rcvr, cat);
        this.sciCatCombo.setValue(cat);
    },

    // When ever a new filter parameter is applied, we need to
    // clear the filter, but then *reapply* any other appropriate filters
    resetFilter: function(pcode, rcvr, cat) {
        var store = this.getStore('Sessions');
        if (store.isFiltered()){
            store.clearFilter();
        }
        this.filterFor(store, 'pcode', pcode);
        this.filterFor(store, 'receivers', rcvr);
        this.filterFor(store, 'sci_categories', cat);
        store.sync();
    },

    // Need this rather then just store.filter because we want 
    // success if our value is *anywhere* found in field.
    filterFor: function(store, field, value) {
        if (value != null & value != '') {
            store.filter([{
                filterFn: function(item) {
                    return item.get(field).search(value) > -1;
                }
            }]);    
            
        }    
    }
});
