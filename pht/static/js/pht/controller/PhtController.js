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

    // utilitiy for making sure users are sure they want to reproduce
    confirmDuplicate: function(store, record, title) {
       Ext.Msg.show({
            title: title,
            msg: 'Are you sure?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            scope: this,
            fn: function(id) {
                if (id == 'yes') {
                    // don't use model.copy because that will cause
                    // a PUT, instead of a POST. Instead we create a new
                    // one, then, gasp, copy fields one by one.
                    // TBF: put this in a copyRecord utility function?
                    var newRecord = Ext.create(store.model, {});
                    for (var i=0; i<record.fields.keys.length; i++) {
                        var field = record.fields.keys[i];
                        newRecord.set(field, record.get(field));
                    }
                    // make sure server gives a new one of these
                    newRecord.set('id', '');
                    newRecord.save();
                    store.load();
                }
            }
        });
    },

});
