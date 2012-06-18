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
                    store.remove([record]);
                    store.sync();
                }
            }
        });
    },

    // abstract function
    onDelete: function(records) {
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
                    this.onDelete(records);
                    store.remove(records);
                    // TBF: we need a callback for when the server
                    // is done, so that we can update other related
                    // stores - but there won't be callbacks for sync
                    // until Ext JS 4.1
                    store.sync();
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
                    var newRecord = this.copyRecord(store, record);
                    newRecord.save({
                        callback: function(obj) {
                            store.load();
                        }    
                    });
                }
            }
        });
    },

    copyRecord: function(store, record) {
        // don't use model.copy because that will cause
        // a PUT, instead of a POST. Instead we create a new
        // one, then, gasp, copy fields one by one.
        var newRecord = Ext.create(store.model, {});
        for (var i=0; i<record.fields.keys.length; i++) {
            var field = record.fields.keys[i];
            newRecord.set(field, record.get(field));
        }
        // make sure server gives a new one of these
        newRecord.set('id', '');
        return newRecord;
    },

    // here so it can be overridden by children
    setRecord: function(record, values) {
            record.set(values);
    },

    updateRecord: function(button, selectedRecords, store) {
        console.log('update');
        var win      = button.up('window');
        if (!win) {
            var form = button.up('form');
        } else {
            var form   = win.down('form');
        }
        console.log(form);
        var record = form.getRecord(),
            values   = form.getValues();

        // editing one, or multiple records?
        if (selectedRecords.length <= 1) {

            // don't do anything if this form is actually invalid
            var f = form.getForm();
            if (!(f.isValid())) {
                return;
            }
   
            this.setRecord(record, values);

            // Is this a new record?
            if (record.get('id') == '') {
                // save on the server side 
                record.save({
                    callback: function(obj) {
                        // TBF: just used this object?
                        // when the new record is made on the server side,
                        // retrieve it.
                        store.load({
                            scope   : this,
                            callback: function(records, operation, success) {
                                // now reload the form
                                last = store.getById(store.max('id'));
                                form.loadRecord(last);
                            }
                        });
                    },
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
