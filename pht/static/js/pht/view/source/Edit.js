// Here we use a simple local store, since the allowed state
// on the server side is just a NullBooleanField
var allowedStates = Ext.create('Ext.data.Store', {
    fields: ['type'],
    data: [{type: 'allowed'},
           {type: 'not allowed'},
           {type: 'unknown'}
          ],
});


Ext.define('PHT.view.source.Edit', {
    extend: 'PHT.view.Edit',
    alias : 'widget.sourceedit',
    title : 'Edit Source',

    initComponent: function() {
        this.items = [
            {
                xtype: 'phtform',
                trackResetOnLoad: true,
                items: [
                    {
                        xtype: 'textfield',
                        name : 'target_name',
                        fieldLabel: 'Name',
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                    },{
                        xtype: 'combo',
                        name: 'pcode',
                        fieldLabel: 'PCODE',
                        store : 'Proposals',
                        queryMode: 'local',
                        displayField: 'pcode',
                        valueField: 'pcode',
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                    },{
                        xtype: 'combo',
                        name : 'coordinate_epoch',
                        fieldLabel: 'Coordinate Epoch',
                        store : 'SourceCoordinateEpochs',
                        queryMode: 'local',
                        displayField: 'epoch',
                        valueField: 'epoch',
                    },{
                        xtype: 'combo',
                        name : 'coordinate_system',
                        fieldLabel: 'Coordinate System',
                        store : 'SourceCoordinateSystems',
                        queryMode: 'local',
                        displayField: 'system',
                        valueField: 'system',
                    },{
                        xtype: 'textfield',
                        name : 'ra',
                        fieldLabel: 'RA (Hrs)',
                        vtype: 'hourField',
                    },{
                        xtype: 'textfield',
                        name : 'dec',
                        fieldLabel: 'Dec (Deg)',
                        vtype: 'degreeField',
                    },{
                        xtype: 'textfield',
                        name : 'ra_range',
                        fieldLabel: 'RA Range (Hrs)',
                        vtype: 'hourField',
                    },{
                        xtype: 'textfield',
                        name : 'dec_range',
                        fieldLabel: 'Dec Range (Deg)',
                        vtype: 'degreeField',
                    },{
                        xtype: 'combo',
                        name : 'velocity_units',
                        fieldLabel: 'Velocity Units',
                        store : 'SourceVelocityTypes',
                        queryMode: 'local',
                        displayField: 'type',
                        valueField: 'type',
                    },{
                        xtype: 'numberfield',
                        name : 'velocity_redshift',
                        fieldLabel: 'Velocity Redshift',
                    },{
                        xtype: 'combo',
                        name : 'convention',
                        fieldLabel: 'Convention',
                        store : 'SourceConventions',
                        queryMode: 'local',
                        displayField: 'convention',
                        valueField: 'convention',
                    },{
                        xtype: 'combo',
                        name : 'reference_frame',
                        fieldLabel: 'Reference Frame',
                        store : 'SourceReferenceFrames',
                        queryMode: 'local',
                        displayField: 'frame',
                        valueField: 'frame',
                    },{
                        xtype: 'combo',
                        fieldLabel: 'Allowed',
                        name: 'allowed',
                        store : allowedStates,
                        queryMode: 'local',
                        displayField: 'type',
                        valueField: 'type',
                        allowBlank: false,
                        labelStyle: 'font-weight:bold',
                    },{
                        xtype: 'checkboxfield',
                        fieldLabel: 'Observed',
                        boxLabel: 'Observed',
                        name: 'observed',
                        uncheckedValue: 'false',
                        inputValue: 'true'
                    },{
                        xtype: 'fieldset',
                        title: 'Original PST Values',
                        collapsible: true,
                        collapsed: true,
                        defaults: {
                            fieldCls: "x-pht-formfield-readonly",
                        },    
                        items: [{
                            xtype: 'textfield',
                            name : 'pst_ra',
                            fieldLabel: 'PST RA',
                            readOnly: true,
                        },{
                            xtype: 'textfield',
                            name : 'pst_ra_range',
                            fieldLabel: 'PST RA Range',
                            readOnly: true,
                        },{
                            xtype: 'textfield',
                            name : 'pst_dec',
                            fieldLabel: 'PST Dec',
                            readOnly: true,
                        },{
                            xtype: 'textfield',
                            name : 'pst_dec_range',
                            fieldLabel: 'PST Dec Range',
                            readOnly: true,
                        }]
                    }
                ]
            },

        ];

        // TBF: this child needs to initialize for the parent
        this.buttons = []

        this.callParent(arguments);
    },

});
