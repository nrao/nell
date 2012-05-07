Ext.define('PHT.store.Friends', {
    extend: 'Ext.data.Store',
    model: 'PHT.model.Friend',
    autoLoad: true,
    proxy: {
        type: 'ajax',
        url: '/pht/friends',
        reader: {
            type: 'json',
            root: 'friends',
            successProperty: 'success'
        }
    }
});
