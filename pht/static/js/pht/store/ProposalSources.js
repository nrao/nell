Ext.define('PHT.store.ProposalSources', {
    extend: 'Ext.data.Store',
    model: 'PHT.model.ProposalSource',
    // Not setting the proxy yet.  We do that when a proposals is selected.
});
