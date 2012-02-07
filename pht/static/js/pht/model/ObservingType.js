Ext.define('PHT.model.ObservingType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/proposal/observing/types',
        reader: {
            type: 'json',
            root: 'observing types',
            successProperty: 'success'
        }
    }
});