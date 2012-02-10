Ext.define('PHT.view.Edit', {
    extend: 'Ext.window.Window',
    alias : 'widget.phtedit',
    layout: 'fit',
    autoShow: true,
    plain: true,
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
                text: 'Close',
                scope: this,
                handler: this.close,
            },
        ];

        // stick these buttons in front of whatever buttons
        // the child may have added
        this.buttons = buttons.concat(this.buttons);

        this.callParent(arguments);
   },

});   

