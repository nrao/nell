Ext.define('PHT.view.TimeUtil', {
    extend: 'Ext.Base',

    constructor: function() {
        this.seconds = 60;
    },
    
    addDays: function(days, dt) {
        return dt.setDate(dt.getDate() + days)
    },

    fractionalHours2HrsMinutes: function(hoursFrac) {
        var hours = Math.floor((hoursFrac*this.seconds)/this.seconds);
        if (hours > 0) {
            var minutes = (hoursFrac % hours) * this.seconds;
        } else {
             var minutes = hoursFrac * this.seconds;
        }
        return [hours, minutes]
    },

    addHoursMinutes: function(hrs, mins, dt) {
        dt.setHours(dt.getHours() + hrs);
        dt.setMinutes(dt.getMinutes() + mins);
        return dt;
    },

    overlap: function(start1, end1, start2, end2) {
        return (start1 <= end2) & (start2 < end1)
    },

});
