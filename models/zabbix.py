# -*- coding: utf-8 -*-
import requests
import os
import time
import json
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyzabbix import ZabbixAPI
from models import timestamp
from configparser import ConfigParser

parser = ConfigParser()
parser.read("./config/config.ini")

#Log in Zabbix front-end API
def zabbixLogin(userZabbix, passwordZabbix):
    zabbixLogin=ZabbixAPI(parser.get("Zabbix", "address"))
    zabbixLogin.login(userZabbix, passwordZabbix)
    return zabbixLogin

#User authentication
def userAuthentication(userZabbix, passwordZabbix):
    try:
        authentication=ZabbixAPI(parser.get("Zabbix", "address"))
        authentication.login(userZabbix, passwordZabbix)
        return authentication
    except:
        pass
#-----------------------------------------------------------------------------------#
#----------------------------------Handlers as JSON---------------------------------#
#-----------------------------------------------------------------------------------#
#Hostgroup filtered by his ID
def hostgroupById(userZabbix, passwordZabbix, hostgroupId):
    hostgroupName = zabbixLogin(userZabbix, passwordZabbix).hostgroup.get(groupids=hostgroupId)
    return hostgroupName[0]["name"]

#Host filtered by his ID
def hostById(userZabbix, passwordZabbix, hostid):
    hostName = zabbixLogin(userZabbix, passwordZabbix).host.get(output="extend", hostids=hostid)[0]['name']
    hostName.upper()
    return hostName
    
#All hostgroups
def jsonAllHostgroups(userZabbix, passwordZabbix):
    array = []
    nullObj = {}
    nullObj['id'] = ""
    nullObj['name'] = "Select a hostgroup"
    array.append(nullObj)
    hostgroups=zabbixLogin(userZabbix, passwordZabbix).hostgroup.get(sortfield="name")
    for hostgroup in hostgroups:
        data = {}
        data['id'] = hostgroup.get("groupid")
        data['name'] = hostgroup.get("name")
        array.append(data)
    return array

#All hosts
def jsonAllHosts(userzabbix, passwordZabix, hostgroupId):
    hosts = zabbixLogin(userzabbix, passwordZabix).host.get(groupids=hostgroupId, sortfield="name")
    array = []
    #nullObj = {}
    #nullObj['id'] = ""
    #nullObj['name'] = "Select a host"
    #array.append(nullObj)
    for host in hosts:
        data = {}
        data['id'] = host.get("hostid")
        data['name'] = host.get("name")
        array.append(data)
    return array

#All tags in trigger's host:
def jsonAllTagsInHost(userZabbix, passwordZabbix, hostId):
    triggers=zabbixLogin(userZabbix, passwordZabbix).trigger.get(hostids=hostId, selectTags="extend", output="extend")
    triggersArray = []
    tagArray = []
    count = 0
    for trigger in triggers:
        if len(triggers[count]['tags']) > 1:
            countTags = 0
            while countTags < len(triggers[count]['tags']):
                combination = "{}: {}".format(triggers[count]['tags'][countTags]['tag'], triggers[count]['tags'][countTags]['value'])
                if not combination in triggersArray:
                    triggersArray.append(combination)
                    countTags+=1
                else:
                    countTags+=1
        elif len(triggers[count]['tags']) == 1:
            combination = "{}: {}".format(triggers[count]['tags'][0]['tag'], triggers[count]['tags'][0]['value'])
            if not combination in triggersArray:
                triggersArray.append(combination)
        count+=1
    for tag in triggersArray:
        data = {}
        data['name'] = tag
        tagArray.append(data)
    return tagArray

#All applications in item's hots:
def jsonAllApplicationsInHost(userZabbix, passwordZabbix, hostid):
    items = zabbixLogin(userZabbix, passwordZabbix).item.get(hostids=hostid, output="extend", selectApplications="extend")
    array = []
    for item in items:
        for application in item.get("applications"):
            value = application.get("name")
            if not value in array:
                array.append(value)
            else:
                pass
    newArray = []
    for value in array:
        data = {}
        data["name"] = value
        newArray.append(data)
    return newArray

#All triggers in hostgroup:
def jsonAllTriggersInHostgroup(userZabbix, passwordZabbix, hostgroupid):
    triggers = zabbixLogin(userZabbix, passwordZabbix).trigger.get(groupids=hostgroupid)
    array = []
    for trigger in triggers:
        value = trigger.get("description")
        if not value in array:
            array.append(value)
        else:
            pass
    newArray = []
    for value in array:
        data = {}
        data["description"] = value
        newArray.append(data)
    return newArray

#-----------------------------------------------------------------------------------#
#----------------------------------Handlers as List---------------------------------#
#-----------------------------------------------------------------------------------#
#CustomerList (General)
def allCustomers(userZabbix, passwordZabbix):
    customerList = [
        "",
        "ADIQ",
        "Ailos",
        "Concremat",
        "FURB",
        "GrownOptical",
        "Havan",
        "Interplayers",
        "IURD",
        "JSL",
        "Kuehne Nagel",
        "Leader",
        "Marabraz",
        "Petz",
        "Phosfaz",
        "Rihappy",
        "Rumo",
        "Sascar",
        "Security",
        "Service",
        "Shibata",
        "Terralingua",
        "Zabbix"
    ]
    return customerList

#Customer list (Zabbix request)
def customer(userZabbix, passwordZabbix):
    customerList = []
    customers = zabbixLogin(userZabbix, passwordZabbix).hostgroup.get()
    for customer in customers:
        array = {}
        array["id"] = customer.get("groupid")
        array["name"] = customer.get("name")
        customerList.append(array)
    return customerList

#Customer list
def allReportBooks():
    optionList = [
        "",
        "Availability",
        "CPU",
        "Memory"
    ]
    return optionList

#Macro substitution    
def macroReplacer(firstString, secondString):
    result = ""
    splittedFirstString = firstString.split()
    splittedSecondString = secondString.split()
    for element in splittedFirstString:
        if "{" in element:
            result += splittedSecondString[splittedFirstString.index(element)]
        else:
            result += f"{element}" + " "
    return result

#Convertion time interval in seconds
def totalSecondsInRangeTime(lastMoment, firstMoment):
    difference = lastMoment - firstMoment
    days, seconds = difference.days, difference.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    result = seconds + (minutes * 60) + (hours * 60)
    return result
#-----------------------------------------------------------------------------------#
#--------------------------------------Capacity-------------------------------------#
#-----------------------------------------------------------------------------------#
def jsonCpuCapacity(userZabbix, passwordZabbix, hostid):
    reportRange = timestamp.ReportRange()
    items = zabbixLogin(userZabbix, passwordZabbix).item.get(hostids=hostid)
    capacityArray = []
    collectedValues = []
    timeValues = []
    count = 0
    print(time.time()-86400)
    for item in items:
        if item.get("name") == "Processor load (15 min average all cores)":
            history = zabbixLogin(userZabbix, passwordZabbix).history.get(history=0, itemids=item.get("itemid"), time_till=time.time(), time_from=time.time()-86400)
            averageValue = 0
            maxValue = 0
            for collection in history:
                actualCollection = float(collection.get("value"))
                collectedValues.append(float(collection.get("value")))            
                timeValues.append(reportRange.capacityTime(int(collection.get("clock"))))
                if maxValue < actualCollection:
                    maxValue = actualCollection
                else:
                    pass
                averageValue += actualCollection
                count+=1
            average = averageValue / count
        elif item.get("name") == "Number of CPUs":
            numberCPU = int(item.get("lastvalue"))
        else:
            pass
    obj = {}
    obj["maxValue"] = maxValue
    obj["average"] = average
    obj["numberCPU"] = numberCPU
    obj["collectedValues"] = collectedValues
    obj["timeValues"] = timeValues
    capacityArray.append(obj)
    return capacityArray

def availabilityAnalysis(userZabbix, passwordZabbix, hostgroupid, triggerName, actualValue, lastValue):
    array = []
    hosts=zabbixLogin(userZabbix, passwordZabbix).host.get(groupids=hostgroupid, selectTriggers="extend", monitored_hosts=True)
    for host in hosts:
        data = {}
        data["hostname"] = host.get("host")
        for trigger in host.get("triggers"):
            if trigger.get("description") == triggerName:
                events = zabbixLogin(userZabbix, passwordZabbix).event.get(hostids=host.get("hostid"), objectids=trigger.get("triggerid"), sortfield="clock", output='extend', sortorder='ASC', time_till=actualValue, time_from=lastValue, value=1)
                eventList = []
                if len(events) >= 1:
                    for notOkEvent in events:
                        fullTime = actualValue - lastValue
                        eventData = {}
                        problemTime = int(notOkEvent.get("clock"))
                        if notOkEvent.get("r_eventid") != "0":
                            okTime = int(zabbixLogin(userZabbix, passwordZabbix).event.get(eventids=notOkEvent.get("r_eventid"))[0]["clock"])
                        else:
                            okTime = int(time.time())
                        slaDiference = totalSecondsInRangeTime(datetime.fromtimestamp(okTime), datetime.fromtimestamp(problemTime))
                        eventData["problemTime"] = str(datetime.fromtimestamp(int(problemTime)))
                        eventData["okTime"] = str(datetime.fromtimestamp(int(okTime)))
                        eventData["sla"] = slaDiference * 100 / fullTime
                        eventData["name"] = notOkEvent.get("name")
                        eventList.append(eventData)
                        data["events"] = eventList
                        data["trigger"] = notOkEvent.get("name")
                elif len(events) == 0:
                    data["trigger"] = "Without events"
                data["problem"] = 0
                data["ok"] = 100              
        array.append(data)
    hostQuantity = len(array)
    SLA = 100
    for element in array:
        print(element)
        if element.get("events"):
            for value in element.get("events"):
                element["problem"] += value.get("sla")
            element["ok"] -= element["problem"]
            SLA -= element["problem"]
        else:
            try:
                SLA -= element.get("problem")
            except:
                pass
    return array, SLA

#-----------------------------------------------------------------------------------#
#--------------------------------------Reports--------------------------------------#
#-----------------------------------------------------------------------------------#
#All triggers in host
def jsonAllTriggersInHost(userZabbix, passwordZabbix, hostId, tag):
    triggers=zabbixLogin(userZabbix, passwordZabbix).trigger.get(hostids=hostId,outuput="extend", expandExpression=1, expandDescription=1, selectTags="extend")
    triggersArray = []
    count = 0
    priorityObj = {
            "0":"Not classified",
            "1":"Information",
            "2":"Warning",
            "3":"Average",
            "4":"High",
            "5":"Disaster"
        }
    for trigger in triggers:
        triggerObj = {}
        triggerObj['id'] = triggers[count]['triggerid']
        triggerObj['status'] = triggers[count]['status']
        triggerObj['value'] = triggers[count]['value']
        triggerObj['description'] = triggers[count]['description'].replace("*UNKNOWN*","Trap Variable")
        triggerObj['priority'] = priorityObj[triggers[count]['priority']]
        
        tagList = []
        if len(triggers[count]['tags']) > 1:
            countTags = 0
            while countTags < len(triggers[count]['tags']):
                combination = "{}: {}".format(triggers[count]['tags'][countTags]['tag'], triggers[count]['tags'][countTags]['value'])
                if not combination in triggersArray:
                    tagList.append(combination)
                    countTags+=1
                else:
                    countTags+=1
            triggerObj['tags'] = tagList
        elif len(triggers[count]['tags']) == 1:
            combination = "{}: {}".format(triggers[count]['tags'][0]['tag'], triggers[count]['tags'][0]['value'])
            if not combination in triggersArray:
                tagList.append(combination)
            triggerObj['tags'] = tagList
        else:
            triggerObj['tags'] = "None"        
        
        triggersArray.append(triggerObj)
        count+=1
    if tag == "ALL":
        return triggersArray
    else:
        newArray = []
        for element in triggersArray:
            if tag in element['tags']:
                newArray.append(element)
            else:
                pass
        return newArray

#All hosts informations in hostgroup
def hosts(userZabbix, passwordZabbix, hostgroupId):
    hosts=zabbixLogin(userZabbix, passwordZabbix).host.get(groupids=hostgroupId, selectInterfaces="extend", available=1, ipmi_available=1, jmx_available=1, snmp_available=1, selectTriggers="extend", selectGraphs="extend", selectParentTemplates=1, tls_connect=1, selectApplications="extend", selectItems="extend")
    hostsArray = []
    count = 0
    for host in hosts:
        data = {}
        data["visibleName"] = host.get("name")
        data["hostname"] = host.get("host")
        data["name"] = "{}\n({})".format(host.get("name"), host.get("host"))
        data["interface"] = "{}:{}".format(host.get("interfaces")[0]["ip"], host.get("interfaces")[0]["port"])
        applicationList = []
        for application in host.get("applications"):
            applicationList.append(application.get("name"))
        data['application'] = "\n".join(applicationList)
        data['item'] = len(host.get("items"))
        data['triggers'] = len(host.get("triggers"))
        data['graphs'] = len(host.get("graphs"))
        data['status'] = "Enable" if (host.get("status") == "0") else "Disable"
        
        avaliableList = []
        if hosts[count]['available'] == '1':
            avaliableList.append("ZBX")
        if hosts[count]['available'] == '2':
            avaliableList.append("ZBX Unavailable")

        if hosts[count]['ipmi_available'] == '1':
            avaliableList.append("IMPI")
        if hosts[count]['ipmi_available'] == '2':
            avaliableList.append("IMPI Unavailable")

        if hosts[count]['snmp_available'] == '1':
            avaliableList.append("SNMP")
        if hosts[count]['snmp_available'] == '2':
            avaliableList.append("SNMP Unavailable")

        if hosts[count]['jmx_available'] == '1':
            avaliableList.append("JMX")
        if hosts[count]['jmx_available'] == '2':
            avaliableList.append("JMX Unavailable")
        
        data['availability'] = ", ".join(avaliableList)      
        hostsArray.append(data)
        count+=1
    return hostsArray

def hostgroups(userZabbix, passwordZabbix, hostgroupId):
    hosts=zabbixLogin(userZabbix, passwordZabbix).host.get(groupids=hostgroupId)
    array = []
    for host in hosts:
        data = {}
        data["name"] = host.get("name")
        array.append(data)
    return array

#All items in host
def items(userZabbix, passwordZabbix, hostid, applicationFilter):
    items=zabbixLogin(userZabbix, passwordZabbix).item.get(hostids=hostid, output="extend", expandName="extend", expandExpression="extend", expandDescription="extend", selectApplications="extend", selectTriggers="extend")
    itemsArray = []
    for item in items:
        applicationList = []
        data = {}
        for application in item.get("applications"):
            applicationList.append(application.get("name"))
        data['applicationList'] = applicationList
        data['name'] = item.get("name")
        data['trends'] = item.get("trends")
        data['interval'] = item.get("delay")
        data['history'] = item.get("history")
        data['triggers'] = len(item.get("triggers"))
        data['status'] = "Enable" if (item.get("status") == "0") else "Disable"
        itemsArray.append(data)
    if applicationFilter == "ALL":
        return itemsArray
    else:
        newArray = []
        for element in itemsArray:
            if applicationFilter in element["applicationList"]:
                newArray.append(element)
            else:
                pass
        return newArray

#All events in host
def events(userZabbix, passwordZabbix, hostId, actualValue, lastValue):
    events=zabbixLogin(userZabbix, passwordZabbix).event.get(hostids=hostId, sortfield="clock", output='extend', sortorder='DESC', time_till=actualValue, time_from=lastValue)
    array = []
    valueFilter = { "0":"OK",
                    "1":"PROBLEM"
                    }
    severityFilter = { "0":"Not Classified",
                       "1":"Information",
                       "2":"Warning",
                       "3":"Average",
                       "4":"High",
                       "5":"Disaster"
                       }
    acknowledgeFilter = { "0":"No",
                          "1":"Yes"
                          }
    for event in events:
        data = {}
        clockValue = int(event.get("clock"))
        data['time'] = str(datetime.fromtimestamp(clockValue)) + " (UTC)"
        data['type'] = valueFilter[event.get("value")]
        data['severity'] = severityFilter[event.get("severity")]
        data['trigger'] = event.get("name")
        data['acknowledged'] = acknowledgeFilter[event.get("acknowledged")]
        array.append(data)
    return array

#All zabbix graphs in host
def graphs(userZabbix, passwordZabbix, hostid, firstDateRange, lastDateRange):
    count = 0
    array = []
    graphs = zabbixLogin(userZabbix, passwordZabbix).graph.get(hostids=hostid)
    url = "http://monitoracao.service.com.br/zabbix1/"
    urlLogin = "http://monitoracao.service.com.br/zabbix1/index.php"
    loginData = {
        'name' : userZabbix, 
        'password' : passwordZabbix,
        'autologin' : '1',
        'enter' : 'Sign in'
                }
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0', 
                'Content-type' : 'application/x-www-form-urlencoded'
                }
    loginPage = requests.post(urlLogin, params=loginData, headers=headers)
    for graph in graphs:
        data = {}
        generator = ""
        if graphs[count]['graphtype'] == "3":
            generator = "chart6.php?"
        elif graphs[count]['graphtype'] == "2":
            generator = "chart6.php?"
        elif graphs[count]['graphtype'] == "1": 
            generator = "chart2.php?"
        elif graphs[count]['graphtype'] == "0":
            generator = "chart2.php?"
        else:
            generator = "chart2.php?"
        
        graphUrl = "{}{}graphid={}&from={}&to={}&profileIdx=web.graphs.filter".format(url, generator, str(graphs[count]["graphid"]), firstDateRange, lastDateRange)   
        
        graphReq = requests.get(graphUrl, cookies=loginPage.cookies)

        name = random.randint(1, 70000)

        if not os.path.exists("{}/static/images/temp/{}".format(parser.get("Reports", "graphs_image_temp_path"), userZabbix.replace(".", "_"))):
            os.mkdir("{}/static/images/temp/{}".format(parser.get("Reports", "graphs_image_temp_path"), userZabbix.replace(".", "_")))
        with open("{}/static/images/temp/{}/{}.png".format(parser.get("Reports", "graphs_image_temp_path"), userZabbix.replace(".", "_"), name), 'wb') as f:
            f.write(graphReq.content)
        data["path"] = "../static/images/temp/{}/{}.png".format(userZabbix.replace(".", "_"), name)
        array.append(data)
        count+=1
    return array

#All user in database
def users(userZabbix, passwordZabbix):
    users = zabbixLogin(userZabbix, passwordZabbix).user.get()
    typeFilter = { "1":"Default user",
                   "2":"Administrator",
                   "3":"Super Administrator"
                    }
    array = []
    for user in users:

        data = {}
        data["id"] = user.get("userid")
        data["name"] = user.get("name")
        data["surname"] = user.get("surname")
        data["alias"] = user.get("alias")
        data["type"] = typeFilter[user.get("type")]
        array.append(data)
    return array

#-----------------------------------------------------------------------------------#
#------------------------------------Troubleshoot-----------------------------------#
#-----------------------------------------------------------------------------------#
def unsuportedItems(userZabbix, passwordZabbix, hostgroupid):
    array = []
    hosts = zabbixLogin(userZabbix, passwordZabbix).host.get(output="extend", groupids=hostgroupid)
    statusFilter = { "0":"Enabled",
                     "1":"Disabled"
                    }
    for host in hosts:
        items = zabbixLogin(userZabbix, passwordZabbix).item.get(webitems="extend", hostids=host.get("hostid"), filter={"state":1}, output="extend")
        data = {}
        if len(items) == 0:
            data["host"] = host.get("host")
            data["unsupportedItemsQtd"] = 0
        else:
            unsupportedItemsArray = []
            for item in items:
                unsuportedItemsData = {}
                unsuportedItemsData["itemName"] = item.get("name")
                unsuportedItemsData["itemError"] = item.get("error")
                unsuportedItemsData["status"] = statusFilter[item.get("status")]
                unsupportedItemsArray.append(unsuportedItemsData)
            data["host"] = host.get("host")
            data["unsupportedItemsQtd"] = len(items)
            data["unsupportedItemsList"] = unsupportedItemsArray
        array.append(data)
    return array