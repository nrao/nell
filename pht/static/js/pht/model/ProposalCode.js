Ext.define('PHT.model.ProposalCode', {
    extend: 'Ext.data.Model',
    fields: [ 'id',
              'pcode',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/options?mode=proposal_codes',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'proposal codes',
            successProperty: 'success'
        }
    }
});
