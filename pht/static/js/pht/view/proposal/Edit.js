Ext.define('PHT.view.proposal.Edit', {
    extend: 'PHT.view.FormPanel',
    alias : 'widget.proposaledit',
    title : 'Edit Proposal',

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
        this.friendCombo = Ext.create('Ext.form.field.ComboBox', {
                            name: 'friend_id',
                            forceSelection: true,
                            fieldLabel: 'Friend',
                            store : 'Friends',
                            queryMode: 'local',
                            lastQuery: '',
                            displayField: 'name',
                            valueField: 'id'
                        });
        this.items = [
            {
                // Upper half has two columns
                layout: 'column',
                items:[{
                    // first column
                    columnWidth: 0.333333,
                    border: false,
                    items: [{
                        xtype: 'textfield',
                        name : 'pcode',
                        fieldLabel: 'PCODE',
                        allowBlank: false,
                    },
                    this.piCombo,
                    this.friendCombo,
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
                    },
                    {
                        xtype: 'numberfield',
                        name: 'requested_time',
                        fieldLabel: 'Requested (Hrs)',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                    },
                    {
                        xtype: 'numberfield',
                        name: 'allocated_time',
                        fieldLabel: 'Allocated (Hrs)',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                    },
                    {
                        xtype: 'textfield',
                        name: 'grades',
                        fieldLabel: 'Grades',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                    }],
                },
                {
                    // second column
                    columnWidth: 0.333333,
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
                },
                {
                    // third column
                    columnWidth: 0.333333,
                    border: false,
                    items: [{
                        xtype: 'textfield',
                        fieldLabel: 'DSS Project',
                        name: 'dss_pcode',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                        labelStyle: '',
                    },
                    {
                        xtype: 'checkboxfield',
                        fieldLabel: 'Next Semester Complete?',
                        //boxLabel: 'Next Semester Complete?',
                        name: 'next_sem_complete',
                        uncheckedValue: 'false',
                        inputValue: 'true',
                        labelStyle: '',
                    },
                    {
                        xtype: 'checkboxfield',
                        fieldLabel: 'Currently Complete?',
                        //boxLabel: 'Currently Complete?',
                        name: 'complete',
                        uncheckedValue: 'false',
                        inputValue: 'true',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                        labelStyle: '',
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'DSS Alloted (Hrs)',
                        name: 'dss_total_time',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                        labelStyle: '',
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'Scheduled (Hrs)',
                        name: 'scheduled_time',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                        labelStyle: '',
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'Billed (Hrs)',
                        name: 'billed_time',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                        labelStyle: '',
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'Remaining (Hrs)',
                        name: 'remaining_time',
                        readOnly: true,
                        fieldCls: "x-pht-formfield-readonly",
                        labelStyle: '',
                    }]
                },
                ],
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
                    name: 'obs_type_codes',
                    fieldLabel: 'Observing Types',
                    store: 'ObservingTypes', // MVC baby!
                    queryMode: 'local',
                    displayField: 'type',
                    valueField: 'code',
                    forceSelection: true,
                    allowBlank: false,
                    width: 600,
                },
                {
                    xtype: 'combo',
                    multiSelect: true,
                    name: 'sci_cat_codes',
                    fieldLabel: 'Science Categories',
                    store: 'ScienceCategories', // MVC baby!
                    queryMode: 'local',
                    displayField: 'category',
                    valueField: 'code',
                    forceSelection: true,
                    width: 600,
                },    
                {
                    xtype: 'textarea',
                    name : 'spectral_line',
                    fieldLabel: 'Spectral Line Info',
                    width: 600,
                    height: 50,
                    allowBlank: true,
                    labelStyle: '',
                },    
                {
                    xtype: 'textarea',
                    name : 'abstract',
                    fieldLabel: 'Abstract',
                    width: 600,
                    height: 50,
                    allowBlank: false,
                }],
            },
        ];

        this.buttons = [
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

    prepMultiEditFields: function() {
        var fields = this.getForm().getFields();
        this.blankState = {};
        var me = this;
        fields.each(function(item, index, length) {
            var disabledItems = ['pcode', 'pi_id', 'joint_proposal'];
            if (disabledItems.indexOf(item.getName()) > -1) {
                item.disable();
            }
            me.blankState[item.getName()] = item.allowBlank;
            item.allowBlank = true;
        });
    },

    resetMultiEditFields: function() {
        var fields = this.getForm().getFields();
        var me     = this;
        fields.each(function(item, index, length) {
            var disabledItems = ['pcode', 'pi_id', 'joint_proposal'];
            if (disabledItems.indexOf(item.getName()) > -1) {
                item.enable();
            }
            item.allowBlank = me.blankState[item.getName()];
        });
    },
});
