Ext.define('PHT.view.FormPanel', {
    extend: 'PHT.view.Form',
    border: false,
    trackResetOnLoad: true,
    autoScroll: true,
    fieldDefaults: {
        labelStyle: 'font-weight:bold',
    },

    listeners: {
        // enable the save button when a change is made
        dirtychange: function(form, dirty) {
            if (dirty) {
                this.saveBtn.enable(true);
            } else {
                this.saveBtn.disable(true);
            }
       }
    },

   // assume this get's called AFTER the child's
   initComponent: function() {
   
        this.saveBtn = Ext.create('Ext.Button', {
            text: 'Save',
            action: 'save',
            disabled: true,
        });

        var buttons = [
            this.saveBtn,
            {
                text: 'Cancel',
                scope: this,
                handler: this.cancel,
            },
        ];

        // stick these buttons in front of whatever buttons
        // the child may have added
        this.buttons = buttons.concat(this.buttons);

        this.callParent(arguments);
   },

    cancel: function(button) {
        this.loadRecord(this.record);
    },

    setRecord: function(record){
        this.record = record;
    },


});
