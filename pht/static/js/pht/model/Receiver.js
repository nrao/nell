Ext.define('PHT.model.Receiver', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'name',
             'abbreviation',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/receivers',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'receivers',
            successProperty: 'success'
        }
    }
});
