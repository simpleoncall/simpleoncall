var saveSettings = function(){
    var data = collectSettings();
    var csrf = document.querySelector('#alert-settings-form input[name="csrfmiddlewaretoken"]').value;
    var xhr = new XMLHttpRequest();
    xhr.responseType = "json";
    xhr.open('POST', '/account/save/alert', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("X-CSRFToken", csrf);
    xhr.onreadystatechange = function(data){
        if(xhr.response){
            window.location.reload();
        }
    };
    xhr.send(JSON.stringify(data));
};

var addNewRow = function(){
    var existing = document.querySelector('.alert-setting-row.disabled');
    if(existing){
        var newRow = existing.cloneNode(true);
        newRow.className = 'alert-setting-row';
        newRow.dataset.id = 0;
        var addAlert = document.getElementById('add-alert-row');
        var alertForm = document.getElementById('alert-settings-form');
        alertForm.insertBefore(newRow, addAlert);
    }
};

var collectSettings = function(){
    var data = [];
    var rows = document.querySelectorAll('#alert-settings-form .alert-setting-row');
    for(var i = 0; i < rows.length; ++i){
        var row = rows[i];
        var id = row.dataset.id;
        var selectedIndex = row.querySelector('select').selectedIndex;
        var options = row.querySelectorAll('option');
        var type = options[selectedIndex].value;
        var time = row.querySelector('input[name=alert_time]').value;
        data.push({
            id: parseInt(id),
            type: type,
            time: parseInt(time),
        });
    }

    return data;
};

document.addEventListener('DOMContentLoaded', function(){
    var addAlertRow = document.getElementById('add-alert-row');
    addAlertRow.addEventListener('click', addNewRow);

    var form = document.getElementById('alert-settings-form');
    form.addEventListener('click', function(e){
        var target = e.target;
        var parent = target.parentElement;
        if(parent.classList.contains('remove-alert-row')){
            e.stopPropagation();
            parent.parentElement.remove();
        } else if(target.classList.contains('alert-settings-submit')){
            e.stopPropagation();
            e.preventDefault();
            saveSettings();
        }
    });
});
