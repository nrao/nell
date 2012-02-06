Ext.define('PHT.model.ObservingType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type'
             ],
    proxy: {
        type: 'ajax',
        url: 'proposal/observing/types',
        reader: {
            type: 'json',
            root: 'observing types',
            successProperty: 'success'
        }
    }
});
