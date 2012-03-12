Ext.define('PHT.model.LstPressure', {
    extend: 'Ext.data.Model',
    fields: ['ra',
             'pressure',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/lst_pressure',
        reader: {
            type: 'json',
            root: 'lst_pressure',
            successProperty: 'success'
        }
    }
});
