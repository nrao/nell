Ext.define('PHT.view.period.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.periodlist',
    store : 'Periods', 
    multiSelect: true,

    initComponent: function() {

        /*
        this.authorsFilterText = Ext.create('Ext.form.field.Text', {
            name: 'authors',
            enableKeyEvents: true,
            emptyText: 'Select Authors...',
            listeners: {
                specialkey: function(textField, e, eOpts) {
                    if (e.getKey() == e.ENTER) {
                        var values = textField.getValue().toLowerCase().split(';');
                        var store  = textField.up('proposallist').getStore('Proposals');
                        for (i=0; i < values.length; i++) {
                            author = values[i].toLowerCase();
                            store.filter([{
                                filterFn: function(item) {
                                    return item.get('authors').toLowerCase().search(author) > -1;
                                }
                            }]);
                        }
                    }
                }
            },
        });

        this.pcodeFilterText = Ext.create('PHT.view.proposal.FilterText', {
            name: 'pcodeFilter',
            emptyText: 'Enter PCode...',
            filterField: 'pcode',
        });

        this.titleFilterText = Ext.create('PHT.view.proposal.FilterText', {
            name : 'titleFilter',
            emptyText: 'Enter Title...',
            filterField: 'title',
        });

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.pcodeFilterText,
                this.titleFilterText,
                this.authorsFilterText,
                Ext.create('Ext.button.Button', {
                        text: 'Clear Filters',
                        action: 'clear',
                }),
                { xtype: 'tbseparator' },
                Ext.create('Ext.button.Button', {
                    text: 'Create Proposal',
                    action: 'create',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Edit Proposal(s)',
                    action: 'edit',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Delete Proposal',
                    action: 'delete',
                }),
                { xtype: 'tbseparator' },
                Ext.create('Ext.button.Button', {
                    text: 'Import Proposal',
                    action: 'import',
                }),
            ]
        }];
        
        */

        this.columns = [
            {header: 'ID', dataIndex: 'id', flex: 1},
            {header: 'Session', dataIndex: 'session', width: 200},
            {header: 'Start Date', dataIndex: 'start_date', flex: 1},
            {header: 'Start Time (UTC)', dataIndex: 'start_time', flex: 1},
            {header: 'Duration (Hrs)', dataIndex: 'duration', flex: 1},
        ];

        this.callParent(arguments);
    }
});
