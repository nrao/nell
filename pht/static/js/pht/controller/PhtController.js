Ext.define('PHT.controller.PhtController', {
    extend: 'Ext.app.Controller',
   
    init: function() {
        this.observers = [];
    },

    editSession: function(grid, record) {
        var view = Ext.widget('sessionedit');
        view.down('form').loadRecord(record);        
        this.notifyObservers({session: record, form: view.down('form')});
    },

    addObserver: function(controller) {
        this.observers.push(controller);
    },

    notifyObservers: function(data) {
        for (i = 0; i < this.observers.length; i++){
            this.observers[i].notify(data);
        }
    },

    notify: function(data) {
        console.log('Base notify.  Please implement something!');
    },

    // utility for making sure users know what the fuck they're doing
    confirmDelete: function(store, record, title) {
       Ext.Msg.show({
            title: title,
            msg: 'Are you sure?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            scope: this,
            fn: function(id) {
                if (id == 'yes') {
                    record.destroy();
                    store.remove([record]);
                }
            }
        });
    },
});
