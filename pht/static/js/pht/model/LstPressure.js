Ext.define('PHT.model.LstPressure', {
    extend: 'Ext.data.Model',
    fields: ['LST',
             'Total',
             'Available',
             'Available_Poor',
             'Available_Good',
             'Available_Excellent',
             'Carryover',
             'Carryover_Poor',
             'Carryover_Good',
             'Carryover_Excellent',
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
