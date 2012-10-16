Ext.define('PHT.view.proposal.ProposalSummaryForm', {
    extend: 'PHT.view.proposal.SemesterSomethingForm',
    alias : 'widget.proposalsummaryform',
    title : 'Proposal Summary',
    
    additionalItems: [{
        xtype: 'checkbox',
        fieldLabel: 'Allocated only',
        name: 'allocated',
        id: 'allocated',
        uncheckedValue: 'false',
        inputValue: 'true',
        value: 'true',
        labelStyle: '',
    }],
});
