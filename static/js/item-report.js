var specificApplicationSelect = document.getElementById("specificItemApplication");
var hostSelect = document.getElementById("selectHost");
hostSelect.onchange = function(){
    var host = hostSelect.value;
    fetch("/js-request/applications-by-item/" + host).then(function(response){
        response.json().then(function(data) {
            var applicationsOptionHTML = '';
            for (var application of data.applications) {
                applicationsOptionHTML += '<option value="' + application.name + '">' + application.name + '</option>';
            } specificApplicationSelect.innerHTML = applicationsOptionHTML
        });
    });
};