Ext.define('PHT.view.proposal.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.proposallist',
    store : 'Proposals', 
    multiSelect: true,

    initComponent: function() {
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
        },
        /*
        TBF: Hold for paging
        {
            xtype: 'pagingtoolbar',
            store: 'Proposals',
            dock: 'bottom',
            displayInfo: true
        }
        */
        ];

        this.columns = [
            {header: 'PCODE', dataIndex: 'pcode', flex: 1},
            {header: 'Title', dataIndex: 'title', width: 200},
            {header: 'Proposal Type', dataIndex: 'proposal_type', flex: 1},
            {header: 'Observing Types', dataIndex: 'observing_types', width: 200},
            {header: 'PI', dataIndex: 'pi_name', flex: 1},
            {header: 'Sci. Categories', dataIndex: 'sci_categories', flex: 1},
            {header: 'Requested Hrs', dataIndex: 'requested_time', flex: 1},
            {header: 'Allocated Hrs', dataIndex: 'allocated_time', flex: 1},
            {header: 'Joint Proposal', dataIndex: 'joint_proposal', flex: 1}
        ];

        this.callParent(arguments);
    }
});
