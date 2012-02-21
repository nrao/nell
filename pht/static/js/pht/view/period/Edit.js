Ext.define('PHT.view.period.Edit', {
    extend: 'PHT.view.Edit',
    alias : 'widget.periodedit',
    title : 'Edit Period',

    initComponent: function() {
        this.items = [
            {
                xtype: 'phtform',
                trackResetOnLoad: true,
                fieldDefaults : {
                    allowBlank: false,
                    labelStyle: 'font-weight:bold',
                },
                items: [
                    {
                        xtype: 'textfield',
                        name : 'session',
                        fieldLabel: 'Session',
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                        readOnly: true,
                    },{
                        xtype: 'datefield',
                        name: 'start_date',
                        fieldLabel: 'Start Date',
                    },{
                        xtype: 'textfield',
                        name: 'start_time',
                        fieldLabel: 'Start Time',
                        vtype: 'hoursMinutes',
                    },{
                        xtype: 'numberfield',
                        name: 'duration',
                        fieldLabel: 'Duration (Hrs)',
                        min: 0,
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                    }
                    /*
                    },{
                        xtype: 'combo',
                        name: 'pcode',
                        fieldLabel: 'PCODE',
                        store : 'ProposalCodes',
                        queryMode: 'local',
                        displayField: 'pcode',
                        valueField: 'pcode',
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                    */    
                ]
            },

        ];

        // TBF: this child needs to initialize for the parent
        this.buttons = []

        this.callParent(arguments);
    },

});
