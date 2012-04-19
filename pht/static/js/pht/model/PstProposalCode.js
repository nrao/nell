Ext.define('PHT.model.PstProposalCode', {
    extend: 'Ext.data.Model',
    fields: ['pcode',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/pst/pcodes',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'pst pcodes',
            successProperty: 'success'
        }
    }
});
