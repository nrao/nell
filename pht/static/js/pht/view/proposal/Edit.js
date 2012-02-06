Ext.define('PHT.view.proposal.Edit', {
    extend: 'Ext.window.Window',
    alias : 'widget.proposaledit',

    title : 'Edit Proposal',
    layout: 'fit',
    autoShow: true,
    plain: true,
    //constrain: true,

    initComponent: function() {
        this.piCombo = Ext.create('Ext.form.field.ComboBox', {
                            name: 'pi_id',
                            fieldLabel: 'Primary Investigator',
                            store : 'PrimaryInvestigators',
                            queryMode: 'local',
                            lastQuery: '',
                            displayField: 'name',
                            valueField: 'id'
                        });
        this.items = [
            {
                xtype: 'form',
                border: false,
                fieldDefaults: {
                    labelStyle: 'font-weight:bold',
                },
                items: [{
                    // Upper half has two columns
                    layout: 'column',
                    items:[{
                        // first column
                        columnWidth: 0.5,
                        border: false,
                        items: [{
                            xtype: 'textfield',
                            name : 'pcode',
                            fieldLabel: 'PCODE',
                            allowBlank: false,
                        },
                        this.piCombo,
                        {
                            xtype: 'combo',
                            name: 'semester',
                            fieldLabel: 'Semester',
                            store: 'Semesters', // MVC baby!
                            queryMode: 'local',
                            displayField: 'semester',
                            valueField: 'semester',
                            forceSelection: true,
                            allowBlank: false,
                        }],
                    },
                    {
                        // second column
                        columnWidth: 0.5,
                        border: false,
                        items: [{
                            xtype: 'combo',
                            name: 'status',
                            fieldLabel: 'Status',
                            store : 'Statuses',
                            queryMode: 'local',
                            displayField: 'name',
                            valueField: 'name',
                            allowBlank: false,
                        },    
                        {
                            xtype: 'combo',
                            name: 'proposal_type',
                            fieldLabel: 'Proposal Type',
                            store : 'ProposalTypes', // MVC baby!
                            queryMode: 'local',
                            displayField: 'type',
                            valueField: 'type',
                            allowBlank: false,
                        },    
                        {
                            xtype: 'datefield',
                            anchor: '100%',
                            fieldLabel: 'Submit Date',
                            name: 'submit_date',
                            allowBlank: false,
                        },
                        {
                            xtype: 'checkboxfield',
                            fieldLabel: 'Joint Proposal',
                            boxLabel: 'Joint Proposal',
                            name: 'joint_proposal',
                            uncheckedValue: 'false',
                            inputValue: 'true'
    
                        }]
                    }],    
                },
                {
                    // lower half is for wider widgets
                    border: false,
                    items:[{
                        xtype: 'textfield',
                        name : 'title',
                        fieldLabel: 'Title',
                        width: 600,
                        allowBlank: false,
                    },
                    {
                        xtype: 'combo',
                        multiSelect: true,
                        name: 'observing_types',
                        fieldLabel: 'Observing Types',
                        store: 'ObservingTypes', // MVC baby!
                        queryMode: 'local',
                        displayField: 'type',
                        valueField: 'type',
                        forceSelection: true,
                        allowBlank: false,
                        width: 600,
                    },
                    {
                        xtype: 'combo',
                        multiSelect: true,
                        name: 'sci_categories',
                        fieldLabel: 'Science Categories',
                        store: 'ScienceCategories', // MVC baby!
                        queryMode: 'local',
                        displayField: 'category',
                        valueField: 'category',
                        forceSelection: true,
                        width: 600,
                    },    
                    {
                        xtype: 'textarea',
                        name : 'abstract',
                        fieldLabel: 'Abstract',
                        width: 600,
                        height: 300,
                        allowBlank: false,
                    }]
                }],
            },
        ];

        this.buttons = [
            {
                text: 'Save',
                action: 'save'
            },
            {
                text: 'Close',
                scope: this,
                handler: this.close,
            },
            {
                text: 'Sessions',
                action: 'sessions'
            },
            {
                text: 'Sources',
                action: 'sources'
            },
            {
                text: 'Authors',
                action: 'authors'
            },
        ];

        this.callParent(arguments);
    },

    filterPis: function(pcode) {
        var pistore = this.piCombo.getStore();
        if (pistore.isFiltered()){
            pistore.clearFilter();
        }
        pistore.filter("pcode", pcode);
        pistore.sort("name");
    },
});
