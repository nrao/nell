Ext.define('PHT.store.Sessions', {
    extend: 'Ext.data.Store',
    model: 'PHT.model.Session',
    autoLoad: true,
    proxy: {
        type: 'rest',
        url: 'sessions',
        reader: {
            type: 'json',
            root: 'sessions',
            successProperty: 'success'
        }
    }
});
