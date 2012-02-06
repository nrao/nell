Ext.define('PHT.model.ScienceCategory', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'category'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/proposal/science/categories',
        reader: {
            type: 'json',
            root: 'science categories',
            successProperty: 'success'
        }
    }
});
