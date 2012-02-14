Ext.define('PHT.view.author.Edit', {
    extend: 'Ext.window.Window',
    alias : 'widget.authoredit',

    title : 'Edit Author',
    layout: 'fit',
    autoShow: true,
    plain: true,
    //constrain: true,

    initComponent: function() {
        var me = this;
        this.pcodeCB = Ext.create('Ext.form.field.ComboBox',
            {
                name: 'pcode',
                fieldLabel: 'PCODE',
                store: 'ProposalCodes',
                queryMode: 'local',
                displayField: 'pcode',
                valueField: 'pcode',
                forceSelection: true,
                allowBlank: false,
                labelStyle: 'font-weight:bold',
            });
        this.items = [
            {
                xtype: 'form',
                defaults: {
                    labelStyle: 'font-weight:bold',
                },
                items: [
                    this.pcodeCB,
                    {
                        xtype: 'combo',
                        name: 'pst_person_id',
                        fieldLabel: 'PST User',
                        store: 'PstUsers',
                        queryMode: 'local',
                        displayField: 'name',
                        valueField: 'person_id',
                        forceSelection: true,
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                        listeners: {
                            select: function(combo, record, index) {
                                Ext.Ajax.request({
                                    url: '/pht/pst/user/info',
                                    params: {
                                        person_id: combo.getValue()
                                    },
                                    method: 'GET',
                                    success: function(response) {
                                        var json = eval('(' + response.responseText + ')');
                                        var author = Ext.create('PHT.model.Author', 
                                            {pcode : me.pcodeCB.getValue()
                                           , pst_person_id : combo.getValue()
                                           , last_name : json.info.lastName
                                           , first_name : json.info.firstName
                                           , affiliation : json.info.affiliation
                                           , email : json.info.email
                                           , telephone : json.info.phone
                                           , address : json.info.address
                                           , professional_status : json.info.personType
                                        });
                                        me.down('form').loadRecord(author);
                                    },
                                });
                            }
                        }
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
                        name : 'telephone',
                        fieldLabel: 'Telephone',
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
