Ext.define('PHT.view.proposal.Allocate', {
    extend: 'PHT.view.Edit',
    alias : 'widget.proposalallocate',
    title : 'Allocate for Proposal',
    autoscroll: true,
    initComponent: function() {

        this.items = [{
            xtype: 'phtform',
            autoScroll: true,
            border: false,
            trackResetOnLoad: true,
            fieldDefaults: {
               labelStyle: 'font-weight:bold',
            },
            items: [{
                xtype: 'numberfield',
                name: 'time_scale',
                fieldLabel: 'Percentage Time',
                minValue: 0.0,
            },{
                xtype: 'combo',
                name: 'grade',
                fieldLabel: 'Grade',
                store: 'SessionGrades', // MVC baby!
                queryMode: 'local',
                displayField: 'grade',
                valueField: 'grade',
                forceSelection: true,
                allowBlank: true
            }],
        }],    

       // must init for parent class
        this.buttons = [];

        this.callParent(arguments);
    },

    setProposal: function(pcode) {
        this.pcode = pcode
    },
});    



