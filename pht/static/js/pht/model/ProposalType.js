Ext.define('PHT.model.ProposalType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/proposal/types',
        reader: {
            type: 'json',
            root: 'proposal types',
            successProperty: 'success'
        }
    }
});
