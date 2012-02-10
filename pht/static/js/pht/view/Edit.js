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
   
        console.log('in Edit.js');
        console.log(this.buttons);
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

        this.buttons = buttons.concat(this.buttons);
        console.log('done in Edit.js');
        console.log(this.buttons);

        this.callParent(arguments);
   },

});   

