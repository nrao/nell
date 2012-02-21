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
    }
});
