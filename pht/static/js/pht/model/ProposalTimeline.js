Ext.define('PHT.model.ProposalTimeline', {
    extend: 'Ext.data.Model',
    fields: ['date',
             'hrs',
             'allocated',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/proposal_timeline',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'timeline',
            successProperty: 'success'
        }
    }
});
