// This is a misnomer, but 'Sponsor' as a model/store name causes problems.
// TBF: why can't the 'Sponsors' store name be found?
Ext.define('PHT.model.Partner', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'name',
             'abbreviation',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/sponsors',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'sponsors',
            successProperty: 'success'
        }
    }             
});
