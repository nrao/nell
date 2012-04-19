Ext.define('PHT.view.plot.LstReportWindow', {
    extend: 'Ext.window.Window',
    alias : 'widget.lstreportwindow',
    title : 'LST Pressure Report',
    autoscroll: true,
    initComponent: function() {

         this.sessionCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'session',
            store: 'Sessions',
            queryMode: 'local',
            lastQuery: '',
            displayField: 'name',
            valueField: 'id',
            emptyText: 'Select a session...',
            fieldLabel: 'Session'
        });

        this.items = [{
            xtype: 'form',
            autoScroll: true,
            border: false,
            items: [{
                xtype: 'checkboxfield',
                name: 'debug',
                fieldLabel: 'Debug?',
                uncheckedValue: 'false',
                inputValue: 'true',
                labelAlign: 'left',
            },
            this.sessionCombo
            ],
        }];    

        this.saveBtn = Ext.create('Ext.Button', {
            text: 'OK',
            action: 'ok',
        });

        this.buttons = [
            this.saveBtn,
            {
                text: 'Cancel',
                scope: this,
                handler: this.hide,
            },
        ];

        this.callParent(arguments);
    },

});    

