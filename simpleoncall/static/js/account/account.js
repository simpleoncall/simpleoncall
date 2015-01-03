var getNextIndex = function(){
    var rows = document.querySelectorAll('.alert-setting-row');
    return rows.length;
};

var addNewRow = function(){
    var index = getNextIndex();
    var existing = document.querySelector('.alert-setting-row');
    var newRow = existing.cloneNode(true);
    newRow.className = 'alert-setting-row';
    setIndex(newRow, index);
    var addAlert = document.getElementById('add-alert-row');
    var alertForm = document.getElementById('alert-settings-form');
    alertForm.insertBefore(newRow, addAlert);
};

var setIndex = function(elm, index){
    elm.dataset.index = index;
    elm.getElementsByTagName('select')[0].name = 'alert_type_' + index;
    elm.getElementsByTagName('input')[0].name = 'alert_time_' + index;
    elm.getElementsByTagName('span')[0].dataset.index = index;
};

var removeRow = function(index){
    var elm = document.querySelector('.alert-setting-row[data-index="' + index + '"]');
    // do not remove disabled rows (like the first row)
    if(elm.className.indexOf('disabled') < 0){
        elm.remove();
    }
    rebalanceIndexes();
};

var rebalanceIndexes = function(){
    var rows = document.querySelectorAll('.alert-setting-row');
    for(var i = 0; i < rows.length; ++i){
        var elm = rows[i];
        if(elm.dataset.index != i){
            setIndex(elm, i);
        }
    }
};

document.addEventListener('DOMContentLoaded', function(){
    var addAlertRow = document.getElementById('add-alert-row');
    addAlertRow.addEventListener('click', addNewRow);

    var form = document.getElementById('alert-settings-form');
    form.addEventListener('click', function(e){
        var parent = e.target.parentElement;
        if(parent.className.indexOf('remove-alert-row') >= 0){
            e.stopPropagation();
            removeRow(parent.dataset.index);
        }

    });
});
