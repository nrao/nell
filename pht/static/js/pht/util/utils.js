
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



