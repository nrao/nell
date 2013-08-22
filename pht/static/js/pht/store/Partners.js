// This is a misnomer, but 'Sponsor' as a model/store name causes problems.
// TBF: why can't the 'Sponsors' store name be found?
Ext.define('PHT.store.Partners', {
    extend: 'Ext.data.Store',
    model: 'PHT.model.Partner',
    autoLoad: true,
});
