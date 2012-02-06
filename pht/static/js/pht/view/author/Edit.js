Ext.define('PHT.view.author.Edit', {
    extend: 'Ext.window.Window',
    alias : 'widget.authoredit',

    title : 'Edit Author',
    layout: 'fit',
    autoShow: true,
    plain: true,
    //constrain: true,

    initComponent: function() {
        this.items = [
            {
                xtype: 'form',
                defaults: {
                    labelStyle: 'font-weight:bold',
                },
                items: [
                    {
                        xtype: 'combo',
                        name: 'pcode',
                        fieldLabel: 'PCODE',
                        store: 'ProposalCodes', // MVC baby!
                        queryMode: 'local',
                        displayField: 'pcode',
                        valueField: 'pcode',
                        forceSelection: true,
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                    },
                    {
                        xtype: 'combo',
                        name: 'pst_person_id',
                        fieldLabel: 'PST User',
                        store: 'PstUsers', // MVC baby!
                        queryMode: 'local',
                        displayField: 'name',
                        valueField: 'person_id',
                        forceSelection: true,
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                    },
                    {
                        xtype: 'textfield',
                        name : 'last_name',
                        fieldLabel: 'Last Name',
                        width: 300,
                        allowBlank: false,
                    },
                    {
                        xtype: 'textfield',
                        name : 'first_name',
                        fieldLabel: 'First Name',
                        width: 300,
                        allowBlank: false,
                    },
                    {
                        xtype: 'textfield',
                        name : 'affiliation',
                        fieldLabel: 'Affiliation',
                        width: 300,
                        allowBlank: false,
                    },
                    {
                        xtype: 'textfield',
                        name : 'email',
                        fieldLabel: 'Email',
                        width: 300,
                        allowBlank: false,
                    },
                    {
                        xtype: 'textfield',
                        name : 'address',
                        fieldLabel: 'Address',
                        width: 300,
                    },
                    {
                        xtype: 'textfield',
                        name : 'telesphone',
                        fieldLabel: 'Telesphone',
                        width: 300,
                    },
                    {
                        xtype: 'textfield',
                        name : 'professional_status',
                        fieldLabel: 'Profession Status',
                        width: 300,
                        allowBlank: false,
                    },
                    {
                        xtype: 'checkboxfield',
                        fieldLabel: 'Domestic',
                        boxLabel: 'Domestic',
                        name: 'domestic',
                        uncheckedValue: 'false',
                        inputValue: 'true'

                    },
                    {
                        xtype: 'checkboxfield',
                        fieldLabel: 'Thesis Observing',
                        boxLabel: 'Thesis Observing',
                        name: 'thesis_observing',
                        uncheckedValue: 'false',
                        inputValue: 'true'

                    },
                    {
                        xtype: 'textfield',
                        name : 'graduation_year',
                        fieldLabel: 'Graduation Year',
                        width: 200,
                    },
                    {
                        xtype: 'textfield',
                        name : 'oldauthor_id',
                        fieldLabel: 'oldauthor_id',
                        width: 200,
                        allowBlank: false,
                    },
                    {
                        xtype: 'textfield',
                        name : 'storage_order',
                        fieldLabel: 'Storage Order',
                        width: 200,
                        allowBlank: false,
                    },
                    {
                        xtype: 'textfield',
                        name : 'other_awards',
                        fieldLabel: 'Other Awards ',
                        width: 300,
                    },
                    {
                        xtype: 'checkboxfield',
                        fieldLabel: 'Support Requester',
                        boxLabel: 'Support Requester',
                        name: 'support_requester',
                        uncheckedValue: 'false',
                        inputValue: 'true'

                    },
                    {
                        xtype: 'checkboxfield',
                        fieldLabel: 'Supported',
                        boxLabel: 'Supported',
                        name: 'supported',
                        uncheckedValue: 'false',
                        inputValue: 'true'

                    },
                    {
                        xtype: 'textfield',
                        name : 'budget',
                        fieldLabel: 'Budget',
                        width: 200,
                        allowBlank: false,
                    },
                    {
                        xtype: 'textarea',
                        name : 'assignment',
                        fieldLabel: 'Assignment',
                        width: 400,
                        height: 150,
                    },
                ]
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
        ];

        this.callParent(arguments);
    },
});
