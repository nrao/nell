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
        'session.Edit',
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
            'sessionedit button[action=periods]': {
                click: this.sessionPeriods
            },            
        });        

        this.selectedPeriods = [];
        this.callParent(arguments);
    },

    setPeriodsWindow: function(periodsWindow) {
        this.periodsWindow = periodsWindow;
    },

    sessionPeriods: function(button) {
        var win     = button.up('window');
            form    = win.down('form');
            session = form.getRecord();
        var pcode      = session.get('pcode');
            session_name = session.get('name');
        var handle = session_name + " (" + pcode + ")";    

        this.periodsWindow.down('periodlist').setHandle(handle);
        this.periodsWindow.show();
    
    },

    clearFilter: function(button) {
        var grid = button.up('periodlist');
        grid.clearFilters();
    },


    createPeriod: function(button) {
        var period = Ext.create('PHT.model.Period');
        var view = Ext.widget('periodedit');
        view.down('form').loadRecord(period);
    },

    deletePeriod: function(button) {
        var grid = button.up('grid');
        var periods = grid.getSelectionModel().getSelection();
        this.confirmDeleteMultiple(this.getPeriodsStore(),
                                   periods,
                                   'Deleting Selected Periods'
        );
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
