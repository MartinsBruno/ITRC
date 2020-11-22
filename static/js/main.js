//Selecionar hosts em um hostgroup
var hostgroupSelect = document.getElementById("selectHostgroup");
var hostSelect = document.getElementById("selectHost");
hostgroupSelect.onchange = function(){
    var hostgroup = hostgroupSelect.value;
    fetch('/js-request/hosts-by-hostgroup/' + hostgroup).then(function(response){
        response.json().then(function(data) {
            var optionHTML = '';
            for (var host of data.hosts) {
                optionHTML += '<option value="' + host.id + '">' + host.name + '</option>';
            } hostSelect.innerHTML = optionHTML;
        });
    });
};

function radioStandard(){
    var selectStandard = document.getElementById("selectStandard");
    var inputStartDate = document.getElementById("startDate");
    var inputEndDate = document.getElementById("endDate");
    selectStandard.style.display = "block";
    selectStandard.disabled = false;
    inputStartDate.style.display = "none";
    inputStartDate.disabled = true;
    inputEndDate.style.display = "none";
    inputEndDate.disabled = true;
}

function radioCustom(){
    var selectStandard = document.getElementById("selectStandard");
    var inputStartDate = document.getElementById("startDate");
    var inputEndDate = document.getElementById("endDate");
    selectStandard.style.display = "none";
    selectStandard.disabled = true;
    inputStartDate.style.display = "block";
    inputStartDate.disabled = false;
    inputEndDate.style.display = "block";
    inputEndDate.disabled = false;
}

function radioAllTriggerTags(){
    var specificTagSelect = document.getElementById("specificTagSelect");
    var selectAllTriggerTags = document.getElementById("selectAllTriggerTags");
    specificTagSelect.style.display = "none";
    specificTagSelect.disabled = true;
    selectAllTriggerTags.style.display = "block";
    selectAllTriggerTags.disabled = false;
}

function radioSpecificTriggerTag(){
    var specificTagSelect = document.getElementById("specificTagSelect");
    var selectAllTriggerTags = document.getElementById("selectAllTriggerTags");
    specificTagSelect.style.display = "block";
    specificTagSelect.disabled = false;
    selectAllTriggerTags.style.display = "none";
    selectAllTriggerTags.disabled = true;
}

function radioAllItemsApplications(){
    var specificApplicationSelect = document.getElementById("specificItemApplication");
    var selectAllApplicationTags = document.getElementById("selectAllItemApplications");
    specificApplicationSelect.style.display = "none";
    specificApplicationSelect.disabled = true;
    selectAllApplicationTags.style.display = "block";
    selectAllApplicationTags.disabled = false;
}

function radioSpecificItemsApplications(){
    var specificApplicationSelect = document.getElementById("specificItemApplication");
    var selectAllApplicationTags = document.getElementById("selectAllItemApplications");
    specificApplicationSelect.style.display = "block";
    specificApplicationSelect.disabled = false;
    selectAllApplicationTags.style.display = "none";
    selectAllApplicationTags.disabled = true;
}