Ext.define('PHT.view.session.Form', {
    extend: 'PHT.view.Form',
    alias:  'widget.sessionform',
    bodyStyle:'padding:5px',
    trackResetOnLoad: true,
    width: 600,
    fieldDefaults: {
        labelAlign: 'top',
        msgTarget: 'side'
    },
    defaults: {
        anchor: '90%',
        border: false
    },
    items: [{
        // First, all basic parameters, in two columns
        layout: 'column',
        border: false,
        items:[{
            // First Column
            columnWidth: 0.3333,
            border: false,
            layout: 'anchor',
            items: [{
                xtype: 'textfield',
                name: 'name',
                fieldLabel: 'Name',
                allowBlank: false,
                labelStyle: 'font-weight:bold',
            },{
                xtype: 'combo',
                name: 'pcode',
                fieldLabel: 'PCODE',
                store: 'ProposalCodes', // MVC baby!
                queryMode: 'local',
                displayField: 'pcode',
                valueField: 'pcode',
                forceSelection: true,
                allowBlank: false,
                labelStyle: 'font-weight:bold',
            },{
                xtype: 'combo',
                name: 'semester',
                fieldLabel: 'Semester',
                store: 'Semesters', // MVC baby!
                queryMode: 'local',
                displayField: 'semester',
                valueField: 'semester',
                forceSelection: true,
                allowBlank: false,
                labelStyle: 'font-weight:bold',
            },{    
                xtype: 'combo',
                name: 'session_type',
                fieldLabel: 'Session Type',
                store: 'SessionTypes', // MVC baby!
                queryMode: 'local',
                displayField: 'type',
                valueField: 'type',
                forceSelection: true,
                allowBlank: false,
                labelStyle: 'font-weight:bold',
            },{    
                xtype: 'combo',
                name: 'weather_type',
                fieldLabel: 'Weather Type',
                store: 'WeatherTypes', // MVC baby!
                queryMode: 'local',
                displayField: 'type',
                valueField: 'type',
                forceSelection: true,
                allowBlank: false,
                labelStyle: 'font-weight:bold',
            }],
           
        },{    
            // Second Column
            columnWidth: 0.333,
            border: false,
            layout: 'anchor',
            items: [{
                xtype: 'combo',
                name: 'grade',
                fieldLabel: 'Grade',
                store: 'SessionGrades', // MVC baby!
                queryMode: 'local',
                displayField: 'grade',
                valueField: 'grade',
                forceSelection: true,
                allowBlank: false,
            },{
                xtype: 'numberfield',
                fieldLabel: 'Requested Time (Hrs)',
                        name: 'requested_time',
            },{
                xtype: 'numberfield',
                fieldLabel: 'Allocated (Hrs)',
                name: 'allocated_time',
            },{
                xtype: 'numberfield',
                fieldLabel: 'Repeats',
                name: 'repeats'
            },{
                xtype: 'numberfield',
                fieldLabel: 'Period (Hrs)',
                name: 'period_time'
            }]    
        },{    
            // Thrids Column
            columnWidth: 0.333,
            border: false,
            layout: 'anchor',
            items: [{
                xtype: 'textfield',
                fieldLabel: 'RA (Hrs)',
                name: 'ra',
                vtype: 'hourField',
            },{
                xtype: 'textfield',
                fieldLabel: 'Dec (Deg)',
                name: 'dec',
                vtype: 'degreeField',
            },{
                xtype: 'textfield',
                fieldLabel: 'Min. LST (Hrs)',
                name: 'min_lst',
                vtype: 'hourField',
            },{
                xtype: 'textfield',
                fieldLabel: 'Max. LST (Hrs)',
                name: 'max_lst',
                vtype: 'hourField',
            },{
                xtype: 'textfield',
                fieldLabel: 'Center LST (Hrs)',
                name: 'center_lst',
                vtype: 'hourField',
            }]
        }],
        // Tabbed by subject
        },{
            xtype: 'tabpanel',
            title: 'Session Details',
            collapsible: true,
            collapsed: false,
            items: [{
                // Allotment Tab
                title: 'Allotment',
                layout: 'column',
                defaults:{bodyStyle:'padding:10px'},
                items: [{
                    // First Column
                    columnwidth: 0.333,
                    border: false,
                    items: [{ 
                        xtype: 'numberfield',
                        fieldLabel: 'Semester (Hrs)',
                        name: 'semester_time',
                    },{
                        xtype: 'numberfield',
                        fieldLabel: 'Interval',
                        name: 'interval_time'
                    }],
                },{
                    // Second Column
                    columnwidth:0.333,
                    border: false,
                    items: [{ 
                        xtype: 'combo',
                        name: 'separation',
                        fieldLabel: 'Separation',
                        store: 'SessionSeparations', // MVC baby!
                        queryMode: 'local',
                        displayField: 'separation',
                        valueField: 'separation',
                        forceSelection: true,
                    },{
                        xtype: 'numberfield',
                        fieldLabel: 'Low Freq (Hrs)',
                        name: 'low_freq_time'
                    }],
                },{
                    // Third Column
                    columnwidth:0.333,
                    border: false,
                    items: [{ 
                        xtype: 'numberfield',
                        fieldLabel: 'High Freq 1 (Hrs)',
                        name: 'hi_freq_1_time'
                    },{
                        xtype: 'numberfield',
                        fieldLabel: 'High Freq 2 (Hrs)',
                        name: 'hi_freq_2_time'
                    }],
                }],    
            },{
                // Target Tab
                title: 'Target',
                layout: 'column',
                defaults:{bodyStyle:'padding:10px'},
                items: [{
                    // First Column
                    columnwidth: 0.5,
                    border: false,
                    items: [{
                        fieldLabel: 'Horizon Limit',
                        name: 'elevation_min',
                        vtype: 'degreeField',
                        xtype: 'textfield',
                    },{
                        fieldLabel: 'LST Width (Hrs)',
                        name: 'LST Width',
                        vtype: 'hourField',
                        xtype: 'textfield',
                    }],    
                },{
                    // Second Column
                    columnwidth: 0.5,
                    border: false,
                    items: [{
                        xtype: 'textfield',
                        fieldLabel: 'LST Exclusion (Hrs)',
                        name: 'lst_ex',
                    },{
                        xtype: 'textfield',
                        fieldLabel: 'LST Inclusion (Hrs)',
                        name: 'lst_in',
                    }]    
                }]
            },{
                title: 'Flags',
                layout: 'column',
                defaults:{bodyStyle:'padding:10px'},
                items: [{
                    // First Column
                    columnwidth: 0.5,
                    border: false,
                    items: [{
                        xtype: 'checkboxfield',
                        name: 'thermal_night',
                        fieldLabel: 'Thermal Night',
                        uncheckedValue: 'false',
                        inputValue: 'true',
                        labelAlign: 'left',
                    },{
                        xtype: 'checkboxfield',
                        name: 'rfi_night',
                        fieldLabel: 'RFI Night',
                        uncheckedValue: 'false',
                        inputValue: 'true',
                        labelAlign: 'left',
                    },{
                        xtype: 'checkboxfield',
                        name: 'optical_night',
                        fieldLabel: 'Optical Night',
                        uncheckedValue: 'false',
                        inputValue: 'true',
                        labelAlign: 'left',
                    }]
                },{
                    // Second column
                    columnwidth: 0.5, 
                    border: false,
                    items: [{
                        xtype: 'checkboxfield',
                        name: 'transit_flat',
                        fieldLabel: 'Transit',
                        uncheckedValue: 'false',
                        inputValue: 'true',
                        labelAlign: 'left',
                    },{
                        xtype: 'checkboxfield',
                        name: 'guaranteed',
                        fieldLabel: 'Guaranteed',
                        uncheckedValue: 'false',
                        inputValue: 'true',
                        labelAlign: 'left',
                    }]                
                }]    
            },{
                title: 'Notes',
                defaults:{bodyStyle:'padding:10px'},
                borders: false,
                items: [{
                    xtype: 'textarea',
                    name: 'scheduler_notes',
                    fieldLabel: 'Scheduler Notes',
                    width: 500,
                    height: 100,
                },{
                    xtype: 'textarea',
                    name: 'constraint_field',
                    fieldLabel: 'Constraint',
                    width: 500,
                    height: 100,
                },{
                    xtype: 'textarea',
                    name: 'comments',
                    fieldLabel: 'Comments',
                    width: 500,
                    height: 100,
                    
                }]
            },{
                title: 'Resources',
                items: [{
                    xtype: 'combo',
                    multiSelect: true,
                    name: 'backends',
                    fieldLabel: 'Backends Requested',
                    store: 'Backends',
                    queryMode: 'local',
                    displayField: 'abbreviation',
                    valueField: 'abbreviation',
                    vtype: 'backendList',
                    labelAlign: 'left',
                    labelWidth: 150,
                    width: 500,
                },{    
                    xtype: 'combo',
                    multiSelect: true,
                    name: 'receivers',
                    fieldLabel: 'Receivers Requested',
                    vtype: 'receiverList',
                    store: 'Receivers',
                    queryMode: 'local',
                    displayField: 'abbreviation',
                    valueField: 'abbreviation',
                    labelAlign: 'left',
                    labelWidth: 150,
                    width: 500,
                },{    
                    xtype: 'combo',
                    multiSelect: true,
                    name: 'receivers_granted',
                    fieldLabel: 'Receivers Granted',
                    vtype: 'receiverList',
                    store: 'Receivers',
                    queryMode: 'local',
                    displayField: 'abbreviation',
                    valueField: 'abbreviation',
                    labelAlign: 'left',
                    labelWidth: 150,
                    width: 500,
                }]
            },{
                title: 'Monitoring',
                items: [{
                    xtype: 'datefield',
                    name: 'start_date',
                    fieldLabel: 'Start Date',
                },{
                    xtype: 'textfield',
                    name: 'start_time',
                    fieldLabel: 'Start Time',
                },{
                    xtype: 'numberfield',
                    name: 'window_size',
                    fieldLabel: 'Window Size',
                },{    
                    xtype: 'numberfield',
                    name: 'outer_window_size',
                    fieldLabel: 'Outer Window Size',
                },{    
                    xtype: 'numberfield',
                    name: 'outer_repeats',
                    fieldLabel: 'Outer Repeats',
                },{    
                    xtype: 'combo',
                    name: 'outer_separation',
                    fieldLabel: 'Outer Separation',
                    //vtype: 'receiverList',
                    store: 'SessionSeparations',
                    queryMode: 'local',
                    valueField: 'separation',
                    displayField: 'separation',
                },{    
                    xtype: 'numberfield',
                    name: 'outer_interval',
                    fieldLabel: 'Outer Repeats',
                },{    
                    xtype: 'textfield',
                    name: 'custom_sequence',
                    fieldLabel: 'Custom Sequence',
                }]    
            },{
                title: 'Misc',
                items: [{
                    xtype: 'checkboxfield',
                    name: 'session_time_calculated',
                    fieldLabel: 'Sess Time Calc',
                    uncheckedValue: 'false',
                    inputValue: 'true',
                    labelAlign: 'left',
                }]    
            },{
                title: 'Original PST Values',
                items: [{
                    xtype: 'textfield',
                    fieldLabel: 'PST Min LST',
                    name: 'pst_min_lst',
                    readOnly: true,
                },{
                    xtype: 'textfield',
                    fieldLabel: 'PST Max LST',
                    name: 'pst_max_lst',
                    readOnly: true,
                },{
                    xtype: 'textfield',
                    fieldLabel: 'PST Horizon Limit',
                    name: 'pst_elevation_min',
                    readOnly: true,
                }]
            }],
        },    
    ],
});             
    
