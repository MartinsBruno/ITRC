var hostSelect = document.getElementById("selectHost");
var tagSelect = document.getElementById("specificTagSelect");
hostSelect.onchange = function(){
    var hostid = hostSelect.value;
    fetch("/js-request/tags-by-trigger/" + hostid).then(function(response){
        response.json().then(function(data) {
            var optionHTML = '';
            for (var tag of data.tags) {
                optionHTML += '<option value="' + tag.name + '">' + tag.name + '</option>';
            } tagSelect.innerHTML = optionHTML
        });
    });
};