Ext.define('PHT.view.period.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.periodlist',
    store : 'Periods', 
    multiSelect: true,

    initComponent: function() {

        this.sessionFilterText = Ext.create('PHT.view.period.FilterText', {
            name: 'sessionFilter',
            emptyText: 'Enter Session (PCODE)...',
            filterField: 'handle',
        });

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.sessionFilterText,
                Ext.create('Ext.button.Button', {
                        text: 'Clear Filters',
                        action: 'clear',
                }),
                { xtype: 'tbseparator' },
                Ext.create('Ext.button.Button', {
                    text: 'Create Period',
                    action: 'create',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Edit Period(s)',
                    action: 'edit',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Delete Period',
                    action: 'delete',
                }),
            ]
        }];
        

        this.columns = [
            {header: 'ID', dataIndex: 'id', flex: 1},
            //{header: 'Proposal', dataIndex: 'pcode', width: 200},
            //{header: 'Session', dataIndex: 'session', width: 200},
            {header: 'Session (PCODE)', dataIndex: 'handle', width: 300},
            {header: 'Start Date', dataIndex: 'start_date', flex: 1},
            {header: 'Start Time (UTC)', dataIndex: 'start_time', flex: 1},
            {header: 'Duration (Hrs)', dataIndex: 'duration', flex: 1},
        ];

        this.callParent(arguments);
    },

    setHandle: function(handle) {
        this.resetFilter(handle);
        this.sessionFilterText.setValue(handle);
    },

    // When ever a new filter parameter is applied, we need to
    // clear the filter, but then *reapply* any other appropriate filters
    resetFilter: function(handle) {
        var store = this.getStore('Periods');
        if (store.isFiltered()){
            store.clearFilter();
        }
        //this.filterFor(store, 'handle', handle);
        store.filter('handle', handle);
        // reapply other filters here
        store.sync();
    },

    // Need this rather then just store.filter because we want 
    // success if our value is *anywhere* found in field.
    filterFor: function(store, field, value) {
        if (value != null & value != '') {
            value = escapeRegEx(value);
            store.filter([{
                filterFn: function(item) {
                    return item.get(field).search(value) > -1;
                }
            }]);    
            
        }    
    },

    // TBF: we need a utility area to put this stuff in 
    escapeRegEx: function(str) {
        // http://kevin.vanzonneveld.net
        // *     example 1: preg_quote("$40");
        // *     returns 1: '\$40'
        // *     example 2: preg_quote("*RRRING* Hello?");
        // *     returns 2: '\*RRRING\* Hello\?'
        // *     example 3: preg_quote("\\.+*?[^]$(){}=!<>|:");
        // *     returns 3: '\\\.\+\*\?\[\^\]\$\(\)\{\}\=\!\<\>\|\:'
    
        return (str+'').replace(/([\\\.\+\*\?\[\^\]\$\(\)\{\}\=\!\<\>\|\:])/g, "\\$1");
    },    

});
