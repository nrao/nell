Ext.define('PHT.view.proposal.ProposalWorksheetForm', {
    extend: 'PHT.view.proposal.SemesterSomethingForm',
    alias : 'widget.proposalworksheetform',
    title : 'Proposal Worksheet',
    
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
