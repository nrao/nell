Ext.define('PHT.view.proposal.ProposalRankingForm', {
    extend: 'PHT.view.proposal.SemesterSomethingForm',
    alias : 'widget.proposalrankingform',
    title : 'Proposal Ranking',
    
    additionalItems: [{
        xtype: 'checkbox',
        fieldLabel: 'Hide Sponsored Proposals',
        name: 'hideSponsors',
        id: 'hideSponsors',
        uncheckedValue: 'false',
        inputValue: 'true',
        value: 'false',
        labelStyle: '',
    }],
});
