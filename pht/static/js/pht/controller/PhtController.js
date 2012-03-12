Ext.define('PHT.controller.PhtController', {
    extend: 'Ext.app.Controller',
   
    init: function() {
        this.observers = [];
    },



    editSession: function(grid, record) {
        var view = Ext.widget('sessionedit');
        view.down('form').loadRecord(record);        
        this.notifyObservers({notification: 'editSession',
                              session: record,
                              form: view.down('form')
        });
    },

    addObserver: function(controller) {
        this.observers.push(controller);
    },

    notifyObservers: function(data) {
        for (var i = 0; i < this.observers.length; i++){
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

    confirmDeleteMultiple: function(store, records, title) {
       Ext.Msg.show({
            title: title,
            msg: 'Are you sure?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            scope: this,
            fn: function(id) {
                if (id == 'yes') {
                    for (i = 0; i < records.length; i++) {
                        records[i].destroy();
                    }
                    store.remove(records);
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

    updateRecord: function(button, selectedRecords, store) {
        var win      = button.up('window'),
            form     = win.down('form'),
            record = form.getRecord(),
            values   = form.getValues();

        // editing one, or multiple records?
        if (selectedRecords.length <= 1) {

            // don't do anything if this form is actually invalid
            var f = form.getForm();
            if (!(f.isValid())) {
                return;
            }
    
            record.set(values);
            // Is this a new session?
            if (record.get('id') == '') {
                record.save();
                //var store = this.getSessionsStore();
                 store.load({
                    scope   : this,
                    callback: function(records, operation, success) {
                        last = store.getById(store.max('id'));
                        form.loadRecord(last);
                    }
                });
            } else {
                // set's the form to not dirty again.
                form.loadRecord(record);
                store.sync();
            }    
        } else {
          
            // multiple records
            var dirty_items = form.getForm().getFieldValues(true);
            // set only those non-blank values that have changed
            real_items = {}
            for (var i in dirty_items) {
                if (values[i] != '') {
                    real_items[i] = values[i];
                }
            }
            // set these values for each selected record
            for (i=0; i < selectedRecords.length; i++) {
                selectedRecords[i].set(real_items);
            }
            store.sync();
            // clean up
            selectedRecords = [];
            win.close();
        }
    },    
    
});
