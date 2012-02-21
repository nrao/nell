Ext.define('PHT.view.overview.PixelsToTime', {
    extend: 'Ext.Base',

    constructor: function() {
        this.hourPx = 60; // # of pixels for an hour
        this.dayPx  = 20; // # of pixels for a day
        this.vertOffset = 10;
        this.horzOffset = 100;
    },

    day2px: function(day) {
        return this.vertOffset + this.dayPx * (day - 1);
    },

    time2px: function(time) {
        // time is in hours
        return this.hourPx * time + this.horzOffset;
    },

    duration2px: function(time) {
        // time is in hours
        return this.hourPx * time;
    },

});
