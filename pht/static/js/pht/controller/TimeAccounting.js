Ext.define('PHT.controller.TimeAccounting', {

    // covers things like when a session's allocated or requested time changes
    // and the proposal needs updating
    updateProposalTime: function(oldValue, newValue, proposal, fieldName) {
        // first, if both new & old values are both NaN, no change, and exit
        if (isNaN(oldValue) && isNaN(newValue)) {
            return
        }

        // otherwise, see if there's been a change
        if (oldValue != newValue) {
            var pTime = proposal.get(fieldName);
            // catch NaN's
            if (!isNaN(oldValue)) {
                pTime = pTime - oldValue
            }
            if (!isNaN(newValue)) {
                pTime = pTime + newValue
            }
            proposal.set(fieldName, pTime);
        }            
    },

    // add or subtract a time from the proposal's time
    updateProposalTimesWorker: function(time, proposal, pField, op) {
            var pValue = parseFloat(proposal.get(pField));
            if (!isNaN(pValue)) {
                pValue = op(pValue, time);
            } else {
                pValue = time;
            }
            proposal.set(pField, pValue);
    },

    // for removing or adding a session from a proposal
    updateProposalTimesFromSession: function(session, proposal, op) {

        // simple enough - we need to add or subtract these new values
        var time = this.getTotalRequestedTime(session);
        if (time != null) {
            this.updateProposalTimesWorker(time
                                         , proposal
                                         , 'requested_time'
                                         , op);
        }    

        var time = this.getTotalAllocatedTime(session);
        if (time != null) {
            this.updateProposalTimesWorker(time
                                         , proposal
                                         , 'allocated_time'
                                         , op);
        }    
    },

    // total = requested * repeats
    getTotalRequestedTime: function(session) {
        var req = parseFloat(session.get('requested_time'));
        var rep = parseFloat(session.get('repeats'));
        return this.calculateRequestedTime(req, rep);
    },

    calculateRequestedTime: function(req, rep) {
        if ((!isNaN(req)) && (!isNaN(rep))) {
            return req * rep;
        } else {
            return null;
        }
    },

    // total = allocated * repeats [ * outer_repeats ]
    getTotalAllocatedTime: function(session) {
        var all = parseFloat(session.get('allocated_time'));
        var rep = parseFloat(session.get('allocated_repeats'));
        var out = parseFloat(session.get('outer_repeats'));
        return this.calculateAllocatedTime(all, rep, out);
    },

    calculateAllocatedTime: function(time, repeats, outer_repeats) {
        var total = null;
        if ((!isNaN(time)) && (!isNaN(repeats))) {
            total = time * repeats; 
        }
        if ((total != null) && (!isNaN(outer_repeats)) && (outer_repeats != 0.0)) {
            total = total * outer_repeats;
        }
        return total;
    },

    // so we can pass in the '+' operator like a function
    add: function(a, b) {
        return a + b;
    },

    
    // so we can pass in the '+' operator like a function (Haskell?)
    sub: function(a, b) {
        return a - b;
    },
    
    // TESTING SECTION ******************************************

    // JS doesn't have an assert; what do we want do do here 
    // during our 'unit' tests?  TBF
    assert: function(expression) {
       if (!expression) {
           console.log('ASSERT FAILED!');
       } else {
           console.log('Pass');
       }
    },

    test: function() {
        console.log('TimeAccounting.test Begin');
        this.testUpdateProposalTimesFromSession();
        this.testUpdateProposalTime();
        this.testGetTotalRequestedTime();
        this.testGetTotalAllocatedTime();
        console.log('TimeAccounting.test End');
    },

    testGetTotalRequestedTime: function() {

        console.log('testGetTotalRequestedTime begin');

        var s = this.createTestSession();

        // sanity check
        this.assert(this.getTotalRequestedTime(s) == 20.0);

        // change stuff
        s.set('repeats', 3);
        this.assert(this.getTotalRequestedTime(s) == 30.0);
        s.set('requested_time', 5);
        this.assert(this.getTotalRequestedTime(s) == 15.0);
        s.set('requested_time', null);
        this.assert(this.getTotalRequestedTime(s) == null);

        console.log('testGetTotalRequestedTime end');
    },    

    testGetTotalAllocatedTime: function() {

        console.log('testGetTotalAllocatedTime begin');

        var s = this.createTestSession();

        // sanity check
        this.assert(this.getTotalAllocatedTime(s) == 20.0);

        // change stuff
        s.set('allocated_repeats', 3);
        this.assert(this.getTotalAllocatedTime(s) == 30.0);
        s.set('allocated_time', 5);
        this.assert(this.getTotalAllocatedTime(s) == 15.0);
        s.set('allocated_time', null);
        this.assert(this.getTotalAllocatedTime(s) == null);
        s.set('allocated_time', 10);
        s.set('allocated_repeats', 2);
        this.assert(this.getTotalAllocatedTime(s) == 20.0);

        // now change the outer repeats
        s.set('outer_repeats', 3);
        this.assert(this.getTotalAllocatedTime(s) == 60.0);
        s.set('outer_repeats', 0);
        this.assert(this.getTotalAllocatedTime(s) == 20.0);
        
        console.log('testGetTotalAllocatedTime end');
    },

    testUpdateProposalTime: function() {

        console.log('testUpdateProposalTime begin');

        var p = this.createTestProposal();

        // sanity check
        this.assert(p.get('requested_time') == 20.0);

        // now check the the no-ops
        this.updateProposalTime(null, null, p, 'requested_time');
        this.assert(p.get('requested_time') == 20.0);

        // now reduce the time
        this.updateProposalTime(20.0, null, p, 'requested_time');
        this.assert(p.get('requested_time') == 0.0);

        // now add the time back
        this.updateProposalTime(null, 20.0, p, 'requested_time');
        this.assert(p.get('requested_time') == 20.0);
       
        // and add a little more
        this.updateProposalTime(20.0, 25.0, p, 'requested_time');
        this.assert(p.get('requested_time') == 25.0);

        // and add a little more
        this.updateProposalTime(25.0, 45.0, p, 'requested_time');
        this.assert(p.get('requested_time') == 45.0);

        // do it all again for allocated time
        f = 'allocated_time'
        this.assert(p.get(f) == 20.0);
        this.updateProposalTime(null, null, p, f);
        this.assert(p.get(f) == 20.0);
        this.updateProposalTime(20.0, null, p, f);
        this.assert(p.get(f) == 0.0);
        this.updateProposalTime(null, 20.0, p, f);
        this.assert(p.get(f) == 20.0);
        this.updateProposalTime(20.0, 25.0, p, f);
        this.assert(p.get(f) == 25.0);

        console.log('testUpdateProposalTime end');
    },

    testUpdateProposalTimesFromSession: function() {

        console.log('testUpdateProposalTimesFromSession begin');
        var s = this.createTestSession();
        var p = this.createTestProposal();
        
        // sanity check
        this.assert(p.get('requested_time') == 20.0);
        this.assert(p.get('allocated_time') == 20.0);

        // test removing the session
        this.updateProposalTimesFromSession(s, p, this.sub);
        this.assert(p.get('requested_time') == 0.0);
        this.assert(p.get('allocated_time') == 0.0);

        // test adding the session back
        this.updateProposalTimesFromSession(s, p, this.add);
        this.assert(p.get('requested_time') == 20.0);
        this.assert(p.get('allocated_time') == 20.0);

        // and adding another one
        this.updateProposalTimesFromSession(s, p, this.add);
        this.assert(p.get('requested_time') == 40.0);
        this.assert(p.get('allocated_time') == 40.0);
        console.log('testUpdateProposalTimesFromSession end');
    },    

        
    createTestSession: function() {
        var s = Ext.create('PHT.model.Session');

        // set requested time
        s.set('requested_time', 10.0);
        s.set('repeats', 2);

        // set allocated time
        s.set('allocated_time', 10.0);
        s.set('allocated_repeats', 2);
        
        return s;
    },

    createTestProposal: function() {
        var p = Ext.create('PHT.model.Proposal');

        // set requested time
        p.set('requested_time', 20.0);

        // set allocated time
        p.set('allocated_time', 20.0);
        
        return p;
    },    
});    
