Ext.define('PHT.view.period.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.periodlist',
    store : 'Periods', 
    multiSelect: true,

    initComponent: function() {
        var grid = this;

        this.util = Ext.create('PHT.view.Util');
        this.timeUtil = Ext.create('PHT.view.TimeUtil');

        this.sessionFilterText = Ext.create('Ext.form.field.Text', {
            name: 'sessionFilter',
            emptyText: 'Enter Session (PCODE)...',
            enableKeyEvents: true,
            listeners: {
                specialkey: function(textField, e, eOpts) {
                    if (e.getKey() == e.ENTER) {
                        grid.setHandle(textField.getValue());
                    }    
                }        
            },
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

    clearFilters: function() {
        var store = this.getStore('Periods');
        if (store.isFiltered()){
            store.clearFilter()
        }
        this.sessionFilterText.reset();
        this.startDateFilter.reset();
        this.daysFilter.reset();
    },

    // When ever a new filter parameter is applied, we need to
    // clear the filter, but then *reapply* any other appropriate filters
    resetFilter: function(handle, startDate, days) {
        var store = this.getStore('Periods');
        if (store.isFiltered()){
            store.clearFilter();
        }
        this.filterFor(store, 'handle', handle);
        if ((startDate != null) & (days != null)) {
            // convert the startDate, days to a time range: need an end date
            var endDate = new Date(startDate);
            endDate = this.timeUtil.addDays(days, endDate);
            store.filter([{
                filterFn: function(period) {
                     // TBF: how to avoid creating this every time?
                     timeUtil = Ext.create('PHT.view.TimeUtil');
                     // does our time range cover this period's? 
                     var periodStartStr = period.get('start_date') + ' ' + period.get('start_time');
                     var periodStart = new Date(periodStartStr); 
                     var periodEnd = new Date(periodStart);
                     var hours = parseFloat(period.get('duration'));
                     var hm = timeUtil.fractionalHours2HrsMinutes(hours);
                     periodEnd = timeUtil.addHoursMinutes(hm[0], hm[1], periodEnd);
                     return timeUtil.overlap(periodStart,
                                                  periodEnd,
                                                  startDate,
                                                  endDate)
    
                }
            }]);        
        }
        store.sync();
    },

    // Need this rather then just store.filter because we want 
    // success if our value is *anywhere* found in field.
    filterFor: function(store, field, value) {
        if (value != null & value != '') {
            value = this.util.escapeRegEx(value);
            store.filter([{
                filterFn: function(item) {
                    return item.get(field).search(value) > -1;
                }
            }]);    
            
        }    
    },

});
