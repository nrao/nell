Ext.define('PHT.store.Sessions', {
    extend: 'Ext.data.Store',
    model: 'PHT.model.Session',
    autoLoad: true,
    pageSize: 50,
    //remoteFilter: true,
    //remoteSort: true,
    proxy: {
        type: 'rest',
        url: '/pht/sessions',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'sessions',
            successProperty: 'success',
            totalProperty: 'total',
        }
    }
});
