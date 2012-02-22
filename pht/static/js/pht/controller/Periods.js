Ext.define('PHT.controller.Periods', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'Period',
        'SessionName',
    ],

    stores: [
        'Periods',
        'SessionNames',
    ],

    views: [
        'period.Edit',
        'period.List',
        'period.ListWindow',
    ],

    init: function() {

        this.control({
            'periodlist' : {
                itemdblclick: this.editPeriod
            },
            'periodlist toolbar button[action=create]': {
                click: this.createPeriod
            },
            'periodlist toolbar button[action=edit]': {
                click: this.editSelectedPeriods
            },
            'periodlist toolbar button[action=delete]': {
                click: this.deletePeriod
            },
            'periodlist toolbar button[action=clear]': {
                click: this.clearFilter
            },
            'periodedit button[action=save]': {
                click: this.updatePeriod
            },            
        });        

        this.selectedPeriods = [];
        this.callParent(arguments);
    },

    clearFilter: function(button) {
        var store = this.getStore('Periods');
        if (store.isFiltered()){
            store.clearFilter()
        }
        var grid = button.up('periodlist');
        grid.sessionFilterText.reset();
    },


    createPeriod: function(button) {
        var period = Ext.create('PHT.model.Period');
        var view = Ext.widget('periodedit');
        view.down('form').loadRecord(period);
    },

    // TBF: refactor up to super class
    deletePeriod: function(button) {
        var grid = button.up('grid');
        var periods = grid.getSelectionModel().getSelection();
        var store  = this.getPeriodsStore();
        Ext.Msg.show({
             title: 'Deleting Selected Periods',
             msg: 'Are you sure?',
             buttons: Ext.Msg.YESNO,
             icon: Ext.Msg.QUESTION,
             scope: this,
             fn: function(id) {
                 if (id == 'yes') {
                     for (i = 0; i < periods.length; i++) {
                         periods[i].destroy();
                     }
                     store.remove(periods);
                 }
             }
        });
    },
    
    editPeriod: function(grid, record) {
        var view   = Ext.widget('periodedit');
        view.down('form').loadRecord(record);        
    },   

    editSelectedPeriods: function(button) {
        var grid = button.up('grid');
        this.selectedPeriods = grid.getSelectionModel().getSelection();

        if (this.selectedPeriods.length <= 1) {
            this.editPeriod(grid, this.selectedPeriods[0]);
        } else {
            var template = Ext.create('PHT.model.Period');
            var view = Ext.widget('periodedit');
            // no field need to be disabled
            view.down('form').loadRecord(template);
        }
    },

    updatePeriod: function(button) {
        this.updateRecord(button
                        , this.selectedPeriods
                        , this.getPeriodsStore()
                         );
        this.selectedPeriods = [];                  
    },

});
