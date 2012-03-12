Ext.define('PHT.model.LstPressure', {
    extend: 'Ext.data.Model',
    fields: ['ra',
             'total',
             'carryover',
             'Poor_A',
             'Poor_B',
             'Poor_C',
             'Good_A',
             'Good_B',
             'Good_C',
             'Excellent_A',
             'Excellent_B',
             'Excellent_C',
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
