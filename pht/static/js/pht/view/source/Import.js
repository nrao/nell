Ext.define('PHT.view.source.Import', {
    extend: 'Ext.window.Window', 
    alias : 'widget.sourceimport',
    title : 'Import Sources',
    layout: 'fit',
    autoShow: true,
    plain: true,

    initComponent: function() {
        this.items = [{
            xtype: 'panel',
            preventHeader: true,
            border: false,
            html: uploadHelp, 
        },{
            xtype: 'form',
            trackResetOnLoad: true,
            border: false,
            items: [{
                xtype: 'filefield',
                allowBlank: false,
                width: 500,
                id: 'form-file',
                emptyText: 'Select a file.',
                fieldLabel: 'File',
                name: 'file',
                buttonText: 'Browse...',
            }],   
        }],
        this.buttons = [{
            text: 'Import',
            action: 'import',
        }]
        this.pcode = '';
        this.callParent(arguments);
    },

    // so that we can tell the server who we're importing for
    setProposalCode: function(pcode) {
        this.pcode = pcode
        this.setTitle("Import Sources for " + pcode);
    },

});

var uploadHelp = '<p><center><bold><font color=red>File Format</center></bold></font></p><br><p>Each line of the file should follow the format:</p><p>SourceName; Group Names; Coordinate System; Equinox; Longitude; Latitude; Ref Frame; Convention; Velocity;</p><p><br><p>For example:</p><p>NGC3242; PNe; Equatorial; J2000; 10:24:46.1; -18:38:32; Barycentric; Optical; 4.70;</p><p>NGC3242 ; PNe ; Equatorial ; J2000 ; 10:24:46.1 ; -18:38:32 ; Barycentric ; Optical ; 4.70;</p><p>NGC3242 Pos1; G1, G2, G3; Equatorial; J2000; 10:24:46.1; -18:38:32; Barycentric; Optical; 4.70;</p><br><br>'


        

