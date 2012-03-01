// need this to find class AM.controller.Users
Ext.Loader.setConfig({enabled:true});

Ext.require(['Ext.form.*']);

Ext.application({
    name: 'PHT',

    appFolder: 'static/js/pht',

    controllers: ['Proposals'
                , 'Authors'
                , 'Dashboard'
                , 'Periods'
                , 'Sources'
                , 'Sessions'
                , 'OverviewCalendar'
                ],

    
    launch: function() {
        var tb = Ext.create('Ext.toolbar.Toolbar');
        var viewport = Ext.create('Ext.container.Viewport', {
            width:  '100%',
            height: '100%',
            title: 'Green Bank Telescope - Proposal Handling Tool',
            layout: 'border',
            defaults: {
                collapsible: true,
                split: true,
                bodyStyle: 'padding:15px'
            },

            items: [
                {
                    region: 'north',
                    xtype: 'panel',
                    margins: '0 0 0 0',
                    cmargins: '0 0 0 0',
                    layout: 'fit',
                    height: 25,
                    collapsible: false,
                    border: false,
                    tbar: tb,
                },
                {
                    title: 'Dash Board (Analysis)',
                    region: 'south',
                    xtype: 'dashboard',
                    id: 'south-region',
                    height: 250,
                    minSize: 75,
                    maxSize: 250,
                    cmargins: '5 0 0 0',
                    collapsed: true,
                },{
                    title: 'Navigation',
                    region:'west',
                    xtype: 'proposalnavigate',
                    margins: '0 0 0 0',
                    cmargins: '0 0 0 0',
                    padding: '0 0 0 0',
                    bodyStyle: 'padding-top: 0px; padding-bottom: 0px',
                    border: 0,
                    width: 200,
                },{
                    collapsible: false,
                    region:'center',
                    margins: '0 0 0 0',
                    layout: 'fit',
                }]
            }
        );

        // render explorers to center 
        var propListWin = Ext.create('PHT.view.proposal.ListWindow', {
            renderTo: viewport.layout.regions.center.getEl(),
        });
        var sessListWin = Ext.create('PHT.view.session.ListWindow', {
            renderTo: viewport.layout.regions.center.getEl(),
        });
        var proposalSources = Ext.create('PHT.view.source.ProposalListWindow', {
            renderTo: viewport.layout.regions.center.getEl(),
        });
        var proposalAuthors = Ext.create('PHT.view.author.ListWindow', {
            renderTo: viewport.layout.regions.center.getEl(),
        });
        var sessionSources = Ext.create('PHT.view.source.SessionListWindow', {
            renderTo: viewport.layout.regions.center.getEl(),
        });
        var overviewCalendar = Ext.create('PHT.view.overview.Calendar', {
            renderTo: viewport.layout.regions.center.getEl(),
        });
        var periodListWin = Ext.create('PHT.view.period.ListWindow', {
            renderTo: viewport.layout.regions.center.getEl(),
        });

        // setup menus
        var importMenu = Ext.create('Ext.menu.Menu', {
            id : 'importMenu',
            items : [{
                text: 'Import Proposal(s)',
                handler: this.getController('Proposals').importProposalFormByProposal
                },
                {
                text: "Import Semester's Proposals",
                handler: this.getController('Proposals').importProposalFormBySemester
                }
            ]
        });
        var toolsMenu = Ext.create('Ext.menu.Menu', {
            id : 'toolsMenu',
            items : [{
                text: 'Proposal Explorer',
                handler: function() {
                    propListWin.show();
                }},
                {
                text: 'Session Explorer',
                handler: function() {
                    sessListWin.show();
                }},
                {
                text: 'Proposal Sources',
                handler: function() {
                    proposalSources.show();
                }},
                {
                text: 'Session Sources',
                handler: function() {
                    sessionSources.show();
                }},
                {
                text: 'Proposal Authors',
                handler: function() {
                    proposalAuthors.show();
                }},
                {
                text: 'Overview Calendar',
                handler: function() {
                    overviewCalendar.show();
                }},
                {
                text: 'Period Explorer',
                handler: function() {
                    periodListWin.show();
                }},
            ]
        });
        var editMenu = Ext.create('Ext.menu.Menu', {
            id : 'editMenu',
            items : [{
                text: 'New',
                menu: Ext.create('Ext.menu.Menu', {
                    id : 'newMenu',
                    items : [{
                        text: 'Proposal',
                        handler: this.createProposal
                        },
                        {
                        text: 'Session',
                        handler: this.createSession
                        }
                    ]
                    })
                }
            ]
        });
        tb.add({
            text: 'Edit',
            menu: editMenu
        });
        tb.add({
            text: 'Tools',
            menu: toolsMenu
        });
        tb.add({
            text: 'Import',
            menu: importMenu
        });
        viewport.layout.regions.center.add(propListWin);
        viewport.layout.regions.center.add(sessListWin);
        viewport.layout.regions.center.add(proposalAuthors);
        viewport.layout.regions.center.add(proposalSources);
        viewport.layout.regions.center.add(sessionSources);
        viewport.layout.regions.center.add(overviewCalendar);
        viewport.layout.regions.center.add(periodListWin);
        propListWin.maximize();
        //overviewCalendar.maximize();
        //overviewCalendar.show();
        this.getController('OverviewCalendar').setOverviewCalendar(overviewCalendar);
        this.getController('Sources').setProposalSourcesWindow(proposalSources);
        this.getController('Sources').setSessionSourcesWindow(sessionSources);
        this.getController('Authors').setProposalAuthorsWindow(proposalAuthors);
        this.getController('Sessions').setSessionListWindow(sessListWin);
        this.getController('Sessions').setPeriodsWindow(periodListWin);
        this.getController('Periods').setPeriodsWindow(periodListWin);
        this.getController('Sessions').addObserver(this.getController('Sources'));
        this.getController('Proposals').addObserver(this.getController('Sources'));
        this.getController('Proposals').addObserver(this.getController('Dashboard'));
        
        // TBF: better place for VTypes?
        // See: http://www.sencha.com/forum/archive/index.php/t-140812.html?s=01edc6b9436d419b2dae5754d39d9e04

        // custom Vtype for vtype:'receiverList'
        Ext.apply(Ext.form.field.VTypes, {
            receiverList: testRcvrs,
            receiverListText: rcvrListText,
        });

        // custom Vtype for vtype:'backendList'
        Ext.apply(Ext.form.field.VTypes, {
            backendList: testBackends,
            backendListText: bckListText,
        });

        // Validate Session's monitoring custome sequence:
        // comma separated list of numbers > zero, starting with one
        Ext.apply(Ext.form.field.VTypes, {
            sessMonitoringCustomSeq:  function(v) {
                var nums = v.split(",");
                for (var i=0; i<nums.length; i++) {
                    var num = parseInt(nums[i]);
                    // don't allow NaNs or zeros
                    if (isNaN(num)) {
                        return false;
                    }
                    if (num == 0) {
                        return false
                    }
                    // make sure first one is one
                    if (i == 0 & num != 1)  {
                        return false 
                    }
                }
                // a list of numbers > 0!
                return true;
            },
            sessMonitoringCustomSeqText: 'Must be a comma separated list of numbers, starting with 1, and never containing zero.',
            sessMonitoringCustomSeqMask: /[\d\,]/i,
        });
         
        // Validate Time in HH:MM format, on quarter boundaries
        var hoursMinutesQtrTest = /^(([2][0-3])|([0-1][0-9]))(:)(00|15|30|45)$/i;
        Ext.apply(Ext.form.field.VTypes, {
            hoursMinutesQtr:  function(v) {

                return hoursMinutesQtrTest.test(v);
            },
            hoursMinutesQtrText: 'Must be a value in Hours, between 0 and 24, in format (HH:MM), on quarter boundaries (00,15,30,45)',
            hoursMinutesQtrMask: /[\d\:]/i,
        });

        // Validate a time duration in hours (on qrt boundaries)
        Ext.apply(Ext.form.field.VTypes, {
            hoursDecimalQtr: function(v) {
                remainder = v % 0.25
                epsilon = 1e-5;
                return (remainder < epsilon);
            },
            hoursDecimalQtrText: 'Must be a value in decimal Hours, on quarter boundaries (.0, .25, .5, .75)',
        });

        // Validates Hour strings in sexigesimal format
        var hourFieldTest = /^(24:00:00.0|(([0]?[0-9]|1[0-9]|2[0-3])(:)([0-5][0-9])(:)([0-5][0-9])(.)([0-9])))$/i;
        Ext.apply(Ext.form.field.VTypes, {
            hourField:  function(v) {

                return hourFieldTest.test(v);
            },
            hourFieldText: 'Must be a value in Hours, between 0 and 24, in sexigesimel format (HH:MM:SS.S)',
            hourFieldMask: /[\d\.\:]/i,
        });

        // Validates Degree strings in sexigesimal format
        // TBF: can't get this style to work
        //var degreeFieldTest = /^([0]?[-][1-9]|1[0-9][0-9]|2[0-9][0-9]|3[0-6][0-9])(:)([0-5][0-9])(:)([0-5][0-9])(.)([0-9]))$/i;
        // but this style allows values > 365 to get through
        var degreeFieldTest = /^-?\d?\d\d:\d\d:\d\d(\.\d)$/i;
        Ext.apply(Ext.form.field.VTypes, {
            degreeField:  function(v) {
                // TBF: also check valid range
                return degreeFieldTest.test(v);
            },
            degreeFieldText: 'Must be a value in Degree, in sexigesimel format (+/- DDD:MM:SS.S)',
            degreeFieldMask: /[\d\.\:\+\-]/i,
        });

    },

    // TBF: should this be in the controller?
    createProposal: function(button) {
        var proposal = Ext.create('PHT.model.Proposal', {});
        var view = Ext.widget('proposaledit');
        view.down('form').loadRecord(proposal);
    },
    createSession: function(button) {
        var session = Ext.create('PHT.model.Session', {});
        var view = Ext.widget('sessionedit');
        view.down('form').loadRecord(session);
    },
});

// Utils

// ['a', 'b'] -> {'a' : '', 'b' : ''}
function makeObjFromList(list) {
    var obj = {}
    for(var i=0; i<list.length; i++)
    {
        obj[list[i]] = ''
    }
    return obj
}    

// TBF: can't believe I have to write this
function hasAllValues(values, validValues) {
    for (i=0; i<values.length; i++) {
        // is this one in our valid list?
        var value = values[i].trim();
        if (!(value in validValues)) {
            return false;
        }
    }
    // all values in list!
    return true;

}

// TBF: should this stuff for validation be a class heirarchy?

// Receiver Validation
// TBF: get this from server? or at least put it in a 'data' dir
var allRcvrs = ['NS','RRI','342','450','600','800','1070','L','S','C','X','Ku','K','Ka','Q','MBA','Z','Hol','KFPA','W']
// Convert our list of strings into both a list and a single string 
var validRcvrs = makeObjFromList(allRcvrs)
var rcvrsStr = allRcvrs.join(',');
var rcvrListText = 'Must be a comma-separated list of receiver abbreviations (i.e. "L,X").  Choices are: ' + rcvrsStr

function testRcvrs(v) {
    // parse the value we're checking
    rcvrs = v.split(",");
    return hasAllValues(rcvrs, validRcvrs);
}

// Backend Validation
// TBF: get this from server? or at least put it in a 'data' dir
var allBcks = ['CCB','CGSR2','DCR','gbtSpec','GASP','GUPPY','HayMark4','Mark5','Mustang', 'Radar','gbtS2','gbtSpecP', 'Vegas','gbtVLBA','Zpect','Other']
var validBcks = makeObjFromList(allBcks);
var backendsStr = allBcks.join(',');
var bckListText = 'Must be a comma-separated list of backend abbreviations (i.e. "gbtSpec,GUPPY").  Choices are: ' + backendsStr

function testBackends(v) {
    // parse the value we're checking
    bs = v.split(",");
    return hasAllValues(bs, validBcks);
}    



