var Hints = {
    values: {}
};

Hints.html = function(cls, html) {
    if (!html)
        return;
    Hints.values[cls] = html;
    var els = Ext.query('.' + cls);
    for (var i = 0; i < els.length; i++) {
        new Ext.ToolTip({
            target: els[i],
            html: html,
            anchor: 'right',
            trackMouse: true,
            showDelay: 0,
            hideDelay: 0,
            dismissDelay: 10000
        });
    }
};

Hints.transition = function(loc_id, html) {
    this.html('loc-tr-' + loc_id, html);
};

Hints.get = function(id) {
    return Hints.values[id];
};

Hints.getTransition = function(id) {
    return Hints.get('loc-tr-' + id);
};

loaded('hints');
