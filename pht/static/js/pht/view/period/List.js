Ext.define('PHT.view.period.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.periodlist',
    store : 'Periods', 
    multiSelect: true,

    initComponent: function() {
        var grid = this;
        this.sessionFilterText = Ext.create('PHT.view.period.FilterText', {
            name: 'sessionFilter',
            emptyText: 'Enter Session (PCODE)...',
            filterField: 'handle',
        });

        this.startDateFilter = Ext.create('Ext.form.field.Date', {
            name: 'startDateFilter',
            emptyText: 'Enter Start Date',
            listeners: {
                select: function(field, value, eOpts) {
                    grid.setStartDate(value);
                },
            },
        });

        this.daysFilter = Ext.create('Ext.form.field.Number', {
            name: 'daysFilter',
            emptyText: 'Enter Days',
            minValue: 1,
            listeners: {
                change: function(field, newValue, oldValue, eOpts) {
                    grid.setDays(newValue);
                },
            },
        });

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.sessionFilterText,
                this.startDateFilter,
                this.daysFilter,
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
            {header: 'Session (PCODE)', dataIndex: 'handle', width: 300},
            {header: 'Start Date', dataIndex: 'start_date', flex: 1},
            {header: 'Start Time (UTC)', dataIndex: 'start_time', flex: 1},
            {header: 'Duration (Hrs)', dataIndex: 'duration', flex: 1},
        ];

        this.callParent(arguments);
    },

    setHandle: function(handle) {
        var startDate = this.startDateFilter.getValue();
        var days = this.daysFilter.getValue();
        this.resetFilter(handle, startDate, days);
        this.sessionFilterText.setValue(handle);
    },

    setStartDate: function(startDate) {
        var handle = this.sessionFilterText.getValue();
        var days = this.daysFilter.getValue();
        this.resetFilter(handle, startDate, days);
    },

    setDays: function(days) {
        var handle = this.sessionFilterText.getValue();
        var startDate = this.startDateFilter.getValue();
        this.resetFilter(handle, startDate, days);
    },

    // When ever a new filter parameter is applied, we need to
    // clear the filter, but then *reapply* any other appropriate filters
    resetFilter: function(handle, startDate, days) {
        // convert the startDate, days to a time range: need an end date
        var endDate = new Date(startDate);
        endDate.setDate(endDate.getDate()+days);
        var store = this.getStore('Periods');
        if (store.isFiltered()){
            store.clearFilter();
        }
        //this.filterFor(store, 'handle', handle);
        store.filter('handle', handle);
        store.filter([{
            filterFn: function(item) {
                 console.log(item.get('start_date'));
                 // convert our item's string start and duration to
                 // a range of date objects
                 // TBF: start_time!!!
                 var itemStart = new Date(item.get('start_date'));
                 // convert fractional hours to int hours & minutes
                 var hoursFrac = parseFloat(item.get('duration'));
                 var hours = Math.floor((hoursFrac*60)/60);
                 if (hours > 0) {
                     var minutes = (hoursFrac % hours) * 60;
                 } else {
                     var minutes = hoursFrac * 60;
                 }
                 var itemEnd = new Date(itemStart);
                 itemEnd.setHours(itemEnd.getHours() + hours);
                 itemEnd.setMinutes(itemEnd.getMinutes() + minutes);
                 //return this.overlap(startDate, endDate, itemStart, itemEnd)
                 return (startDate <= itemEnd) & (itemStart <= endDate)

            }
        }]);        
        //store.filter('start_date', dle);
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
