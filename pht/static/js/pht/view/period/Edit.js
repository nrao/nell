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
                        xtype: 'combo',
                        name : 'handle',
                        fieldLabel: 'Session',
                        store: 'SessionNames',
                        //allowBlank: false,
                        //labelStyle: 'font-weight:bold',
                        displayField: 'handle',
                        valueField: 'handle',
                        queryMode: 'local',
                        width: 400,
                    },{
                        xtype: 'datefield',
                        name: 'start_date',
                        fieldLabel: 'Start Date',
                    },{
                        xtype: 'textfield',
                        name: 'start_time',
                        fieldLabel: 'Start Time',
                        vtype: 'hoursMinutesQtr',
                    },{
                        xtype: 'numberfield',
                        name: 'duration',
                        fieldLabel: 'Duration (Hrs)',
                        minValue: 0,
                        step: 0.25,
                        vtype: 'hoursDecimalQtr',
                        //allowBlank: false,
                        //labelStyle: 'font-weight:bold',
                    }
                ]
            },

        ];

        // TBF: this child needs to initialize for the parent
        this.buttons = []

        this.callParent(arguments);
    },

});
