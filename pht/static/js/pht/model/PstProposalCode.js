Ext.define('PHT.model.PstProposalCode', {
    extend: 'Ext.data.Model',
    fields: ['pcode',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/pst/pcodes',
        reader: {
            type: 'json',
            root: 'pst pcodes',
            successProperty: 'success'
        }
    }
});
