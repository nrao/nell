Ext.define('PHT.store.PstUsers', {
    extend: 'Ext.data.Store',
    model: 'PHT.model.PstUser',
    autoLoad: true,
    proxy: {
        type: 'ajax',
        url: 'pst/users',
        reader: {
            type: 'json',
            root: 'users',
            successProperty: 'success'
        }
    }
});
