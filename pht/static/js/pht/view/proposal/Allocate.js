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
                xtype: 'fieldset',
                title: 'Scaled or Absolute Time?',
                items: [{
                    xtype: 'checkboxfield',
                    fieldLabel: 'Scale?',
                    name: 'scale',
                    uncheckedValue: 'false',
                    inputValue: 'true',
                  },{
                    xtype: 'numberfield',
                    name: 'time',
                    fieldLabel: 'Value',
                    minValue: 0.0,
                  }]    
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
        this.clearBtn = Ext.create('Ext.button.Button', {
            text: 'Clear',
            action: 'clear',
        });

        this.buttons = [this.clearBtn];

        this.callParent(arguments);
    },

    setProposal: function(pcode) {
        this.pcode = pcode
    },
});    



