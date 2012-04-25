Ext.define('PHT.model.ScienceCategory', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'category',
             'code',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/proposal/science/categories',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'science categories',
            successProperty: 'success'
        }
    }
});
