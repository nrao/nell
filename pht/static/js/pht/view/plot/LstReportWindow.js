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
        var carryoverTypes = Ext.create('Ext.data.Store', {
            fields: ['type'],
            data:[
                {'type' : 'Remaining Time'},
                {'type' : 'Next Semester Time'},
                ]
        });        
         this.carryoverTypesCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'carryoverType',
            fieldLabel: 'Carryover',
            store: carryoverTypes,
            queryMode: 'local',
            //lastQuery: '',
            displayField: 'type',
            valueField: 'type',
            value: 'Next Semester Time',
            hideLabel: false,
            editable: false,
            //emptyText: 'Select a carryover type...',
        });
        this.items = [{
            xtype: 'form',
            autoScroll: true,
            border: false,
            items: [{
                xtype: 'checkboxfield',
                name: 'debug',
                fieldLabel: 'Details?',
                uncheckedValue: 'false',
                inputValue: 'true',
                labelAlign: 'left',
            },
            this.sessionCombo,
            this.carryoverTypesCombo,
            {
                xtype: 'checkboxfield',
                name: 'adjustWeatherBins',
                fieldLabel: 'Adjust Weather?',
                uncheckedValue: 'false',
                inputValue: 'true',
                //value : 'checked',
                checked: true,
                labelAlign: 'left',
            },
            {
                xtype: 'checkboxfield',
                name: 'showSponsors',
                fieldLabel: 'Show Sponsors?',
                uncheckedValue: 'false',
                inputValue: 'true',
                //value : 'checked',
                checked: false,
                labelAlign: 'left',
            },
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

