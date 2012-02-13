Ext.define('PHT.view.proposal.PhtFieldSet', {
    extend: 'Ext.form.FieldSet',
    alias: 'widget.phtfieldset',
    initComponent: function() {
        this.addEvents('expand', 'collapse');
        this.callParent([arguments]);
    },
    setExpanded: function(expanded){
        var bContinue;
        if (expanded) {
            bContinue = this.fireEvent('expand', this);
        } else {
            bContinue = this.fireEvent('collapse', this);
        }
        if (bContinue !== false) {
            this.callParent([expanded]);
        }
    }
});
