# -*- coding: utf-8 -*-
from prometheus_flask_exporter import PrometheusMetrics as metrics
from flask import Flask, request, render_template, session, jsonify, redirect, make_response, flash, url_for, send_file
from flask_weasyprint import HTML, render_pdf
from models import timestamp
from models import zabbix
from models import excel
from models import graphTimestamp
from models import fileFormater
from datetime import datetime
from configparser import ConfigParser
from weasyprint import HTML, CSS, default_url_fetcher
import time 
import random
import pygal
import xlwt
import os
import shutil
import zipfile
import io

app = Flask(__name__)
metrics(app)

parser = ConfigParser()
parser.read("./config/config.ini")

#-----------------------------------------------------------------------------------#
#-------------------------------Authentication System-------------------------------#
#-----------------------------------------------------------------------------------#
@app.route("/userList")
def pageFon():
    return jsonify ({'hosts': zabbix.users(session['userName'], session['userPassword'])})
#Index route

@app.route("/")
def pageIndex():
    if 'userName' not in session or session['userName'] == None:
        return redirect('/login')
    return render_template('index.html', 
    title="Service ITRC")

#Login route
@app.route("/login")
def pageLogin():
    return render_template('login.html', 
    title="Service ITRC")

#Authentication route
@app.route("/authentication", methods=["POST", "GET"])
def authentication():
    if request.method == "POST":
        session["userName"] = request.form["inputUsername"]
        session["userPassword"] = request.form["inputPassword"]
        validation = zabbix.userAuthentication(session["userName"], session["userPassword"])
        if validation:
            return make_response(redirect("/"))
        else:
            return redirect("/login")

#Logout route
@app.route('/logout')
def logout():
    session['userName'] = None
    session['userPassword'] = None
    return redirect('/login')

#-----------------------------------------------------------------------------------#
#----------------------------------Administration-----------------------------------#
#-----------------------------------------------------------------------------------#
#User Form
@app.route("/administration/user-form")
def pageUserForm():
    return render_template("user-form.html", 
    title = "User Report",
    name = "User Report")

#User Report (HTML)
@app.route("/administration/user-report", methods=["GET", "POST"])
def pageUserReport():
    #hostgroupid = request.form["selectHostgroup"]
    return render_template("user-report.html",
    title = "User Report",
    userList = zabbix.users(session["userName"], session["userPassword"]))

#User Report (PDF)
@app.route("/administration/user-report-pdf", methods=["GET", "POST"])
def pdfUserReport():
    reportRange = timestamp.ReportRange()
    html = render_template('pdf-user-report.html', 
    title="User Report", 
    name="User Report",
    userList=zabbix.users(session['userName'], session['userPassword']),
    date=reportRange.getActualDateFormated())

    response = make_response(render_pdf(HTML(string=html), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')]))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename='+ 'zabbix-user-list.pdf'                                                     
    return response

#User Report (Excel)
@app.route("/administration/user-report-excel", methods=["GET", "POST"])
def excelUserReport():
    listUsers = zabbix.users(session["userName"], session["userPassword"])
    file = excel.userList("zabbix-user-list.xls", listUsers)
    file.save(f"temp/zabbix-user-list.xls")
    return send_file("temp/zabbix-user-list.xls", as_attachment=True)  
  
#-----------------------------------------------------------------------------------#
#-----------------------------------Availability------------------------------------#
#-----------------------------------------------------------------------------------#
#Availability Analisys
@app.route("/availability/availability-analysis", methods=["GET", "POST"])
def pageAvailabilityAnalysis():
    return render_template("availability-analysis.html", 
    title="Availability Analysis",
    name="Availability Analysis",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]))

#Availability Analisys (Excel)
@app.route("/capacity/availability-analysis-report", methods=["GET", "POST"])
def excelAvailabilityAnalysisReport():
    reportRange = timestamp.ReportRange()
    typeObj = reportRange.rangeModel()
    hostgroupid = request.form["availabilityHostgroup"]

    try:
        if request.form["selectStandard"]:
            formValue = request.form["selectStandard"]
            firstValue = typeObj[formValue][0]
            secondValue = typeObj[formValue][1]
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    except:
        if request.form["startDate"] and request.form["endDate"]:
            firstValue = datetime.strptime(request.form["startDate"]+' 00:00:00', '%Y-%m-%d %H:%M:%S')
            secondValue = datetime.strptime(request.form["endDate"]+' 23:59:59', '%Y-%m-%d %H:%M:%S')
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue

    zabbixRequest = zabbix.availabilityAnalysis(session["userName"], session["userPassword"], hostgroupid, request.form["triggerSelect"], datetime.timestamp(secondValue), datetime.timestamp(firstValue))
    availabilityList = zabbixRequest[0]
    SLA = zabbixRequest[1]
    
    file = excel.availabilityAnalysis(zabbix.hostgroupById(session["userName"], session["userPassword"], hostgroupid), availabilityList, SLA)
    filename = "{}-availability-analysis.xls".format(zabbix.hostgroupById(session["userName"], session["userPassword"], hostgroupid).replace("/", "-"))
    file.save("temp/{}".format(filename))
    path = "temp/{}".format(filename)
    return send_file(path, as_attachment=True)

#-----------------------------------------------------------------------------------#
#---------------------------------------Book----------------------------------------#
#-----------------------------------------------------------------------------------#
#Books Form
@app.route("/book/checklist-form")
def pageBookForm():
    return render_template("checklist-form.html", 
    title = "Checklist Report",
    name = "Checklist Report",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]),
    optionList = zabbix.allReportBooks())

#Books Form (Updated)
@app.route("/books")
def pageBooksForm():
    return render_template("book-form.html", 
    title = "Books",
    name = "Books",
    optionsList = zabbix.AllCustomer(),
    optionList = zabbix.allReportBooks())

#Books Report (HTML)
@app.route("/book/checklist-report", methods=["GET", "POST"])
def pageBookReport():
    hostgroups = request.form.getlist("selectCustomer")
    technology = request.form.get("selectTechnology")
    print(technology)
    reportRange = timestamp.ReportRange()
    rangeModel = reportRange.getPreviousSixMonths()
    if technology == "Availability":
        graph = pygal.Bar(print_values=True)
        graph.x_labels = [rangeElement.get("month") for rangeElement in rangeModel]
        windowsList = []
        for rangeElement in rangeModel:
            print(rangeElement)
            availability = zabbix.availabilityAnalysis(session["userName"], 
                                            session["userPassword"], 
                                            hostgroups[0], 
                                            "Unavailable by ICMP", 
                                            rangeElement.get("end"), 
                                            rangeElement.get("begin"))
            windowsList.append(round(availability[1], 1))
        linuxList = []
        for rangeElement in rangeModel:
            print(rangeElement)
            availability = zabbix.availabilityAnalysis(session["userName"], 
                                            session["userPassword"], 
                                            hostgroups[1], 
                                            "Unavailable by ICMP", 
                                            rangeElement.get("end"), 
                                            rangeElement.get("begin"))
            linuxList.append(round(availability[1], 1))
        graph.add("Windows", windowsList)
        graph.add("Linux", linuxList)
        graph_data = graph.render_data_uri()
        return render_template("checklist-report.html", 
        title="Unavailable by ICMP",
        name=technology,
        graph=graph_data)
    elif technology == "CPU":
        pass

#Books Report (PDF)
@app.route("/book/checklist-report-pdf", methods=["GET", "POST"])
def pagePdfBookReport():
    hostgroups = request.form.getlist("selectCustomer")
    technology = request.form.get("selectTechnology")
    reportRange = timestamp.ReportRange()
    rangeModel = reportRange.getPreviousSixMonths()
    if technology == "Availability":
        graph = pygal.Bar(print_values=True)
        graph.x_labels = [rangeElement.get("month") for rangeElement in rangeModel]
        windowsList = []
        for rangeElement in rangeModel:
            availability = zabbix.availabilityAnalysis(session["userName"], 
                                            session["userPassword"], 
                                            hostgroups[0], 
                                            "Unavailable by ICMP", 
                                            rangeElement.get("end"), 
                                            rangeElement.get("begin"))
            windowsList.append(round(availability[1], 1))
        linuxList = []
        for rangeElement in rangeModel:
            print(rangeElement)
            availability = zabbix.availabilityAnalysis(session["userName"], 
                                            session["userPassword"], 
                                            hostgroups[1], 
                                            "Unavailable by ICMP", 
                                            rangeElement.get("end"), 
                                            rangeElement.get("begin"))
            linuxList.append(round(availability[1], 1))
        graph.add("Windows", windowsList)
        graph.add("Linux", linuxList)
        userFolder = f"{session['userName']} - (books)"
        graphs_image_temp_path = parser.get("Reports", "graphs_image_temp_path")
        fullPath = f"{graphs_image_temp_path}/temp/{userFolder}"
        graph.render_to_png('/temp/availability.png')
        #return send_file("/temp/availability.png", as_attachment=True)
        return "OK"
        

#CPU form
@app.route("/book/cpu", methods=["GET", "POST"])
def pageCapacityCpu():
    return render_template("capacity-cpu.html", 
    title="CPU's Capacity",
    name="CPU's Capacity",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]))

#CPU Report (HTML)
@app.route("/book/cpu-capacity", methods=["GET", "POST"])
def pageCpuReport():
    hostId = request.form["selectHost"]
    itemList = zabbix.jsonCpuCapacity(session["userName"], session["userPassword"], hostId)
    graph = pygal.Line(dots_size=2, x_label_rotation=20, show_minor_x_labels=False)
    graph.x_labels = itemList[0]["timeValues"]
    N = 40
    graph.add("CPU usage", itemList[0]["collectedValues"])
    graph.x_labels_major = itemList[0]["timeValues"][::N]
    graph_data = graph.render_data_uri()
    return render_template("cpu-report.html", 
    title="CPU Capacity",
    name=zabbix.hostById(session["userName"], session["userPassword"], hostId),
    identification=hostId,
    itemList=itemList,
    graph=graph_data)

#CPU Report (PDF)
@app.route('/book/cpu-capacity-pdf', methods=["GET", "POST"])
def pagePdfCpuReport():
    hostId = request.form["selectHost"]
    reportRange = timestamp.ReportRange()
    itemList = zabbix.jsonCpuCapacity(session["userName"], session["userPassword"], hostId)
    graph = pygal.Line(dots_size=2, x_label_rotation=20, show_minor_x_labels=False)
    graph.x_labels = itemList[0]["timeValues"]
    N = 40
    graph.add("CPU usage", itemList[0]["collectedValues"])
    graph.x_labels_major = itemList[0]["timeValues"][::N]
    graph_data = graph.render_data_uri()
    html = render_template('pdf-cpu-report.html', 
    title="Items Report", 
    name=zabbix.hostById(session['userName'], session['userPassword'], hostId),
    itemList=itemList, 
    date=reportRange.getActualDateFormated(),
    graph=graph_data)

    response = make_response(render_pdf(HTML(string=html)))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename='+ '{}_cpu-capacity_{}.pdf'.format(zabbix.hostById(session['userName'], session['userPassword'], hostId).replace("/","-").replace(" ",""), reportRange.getActualDateFormated())                                                      
    return response

#-----------------------------------------------------------------------------------#
#------------------------------------Monitoring-------------------------------------#
#-----------------------------------------------------------------------------------#
#Event Route
@app.route("/monitoring/event-form")
def pageEventForm():
    return render_template("event-form.html", 
    title = "Event Report",
    name = "Event Report",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]))

#Event Report (HTML)
@app.route("/monitoring/event-report", methods=["GET", "POST"])
def pageEventReport():
    array = []
    reportRange = timestamp.ReportRange()
    typeObj = reportRange.rangeModel()
    hostList = request.form.getlist("selectHost")
    try:
        if request.form["selectStandard"]:
            formValue = request.form["selectStandard"]
            firstValue = typeObj[formValue][0]
            secondValue = typeObj[formValue][1]
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    except:
        if request.form["startDate"] and request.form["endDate"]:
            firstValue = datetime.strptime(request.form["startDate"]+' 00:00:00', '%Y-%m-%d %H:%M:%S')
            secondValue = datetime.strptime(request.form["endDate"]+' 23:59:59', '%Y-%m-%d %H:%M:%S')
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    for host in hostList:
        data = {}
        data["name"] = zabbix.hostById(session["userName"], session["userPassword"], host)
        data["infos"] = zabbix.events(session["userName"], session["userPassword"], host, datetime.timestamp(secondValue), datetime.timestamp(firstValue))
        array.append(data)
    return render_template("event-report.html", title="Event Report",
                                                list=array)

#Event Report (PDF)
@app.route('/monitoring/event-report-pdf', methods=["GET", "POST"])
def pagePdfEventReport():
    reportRange = timestamp.ReportRange()
    date = reportRange.getActualDateFormated()
    typeObj = reportRange.rangeModel()
    hostgroup = request.form.get("selectHostgroup")
    hostList = request.form.getlist("selectHost")
    userFolder = f"{session['userName']} - (events)"

    graphs_image_temp_path = parser.get("Reports", "graphs_image_temp_path")
    fullPath = f"{graphs_image_temp_path}/temp/{userFolder}"
    hostgroupName = zabbix.hostgroupById(session['userName'], session['userPassword'], hostgroup)
    
    try:
        if request.form["selectStandard"]:
            formValue = request.form["selectStandard"]
            firstValue = typeObj[formValue][0]
            secondValue = typeObj[formValue][1]
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    except:
        if request.form["startDate"] and request.form["endDate"]:
            firstValue = datetime.strptime(request.form["startDate"]+' 00:00:00', '%Y-%m-%d %H:%M:%S')
            secondValue = datetime.strptime(request.form["endDate"]+' 23:59:59', '%Y-%m-%d %H:%M:%S')
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    
    if len(hostList)>=2:
        if not os.path.exists(fullPath):
            os.mkdir(fullPath)
        else:
            shutil.rmtree(fullPath)
            os.mkdir(fullPath)
        for element in hostList:
            hostname = zabbix.hostById(session['userName'], session['userPassword'], element)
            jsonInformations = zabbix.events(session['userName'], session['userPassword'], element, datetime.timestamp(session['secondValue']), datetime.timestamp(session['firstValue']))
            html = render_template('pdf-event-report.html',title="Events Report", 
                                                           name=zabbix.hostById(session['userName'], session['userPassword'], element),
                                                           eventList=zabbix.events(session['userName'], session['userPassword'], element, datetime.timestamp(session['secondValue']), datetime.timestamp(session['firstValue'])),
                                                           date=reportRange.getActualDateFormated())
            HTML(file_obj=html).write_pdf("{}/{} - (EVENTS).pdf".format(fullPath, fileFormater.modifyHostgroupName(hostname)), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')])
        filePaths = []
        for root, directories, files in os.walk(fullPath):
            for filename in files:
                filePath = os.path.join(root, filename)
                filePaths.append(filePath)
        zip_file = zipfile.ZipFile(f"temp/{userFolder}/{fileFormater.modifyHostgroupName(hostgroupName)}.zip", "w")
        with zip_file:
            for archive in filePaths:
                zip_file.write(archive)
        zip_file.close()
        return send_file(f"temp/{userFolder}/{fileFormater.modifyHostgroupName(hostgroupName)}.zip", as_attachment=True)
    else:
        html = render_template('pdf-event-report.html',title="Events Report", 
                                                    name=zabbix.hostById(session['userName'], session['userPassword'], hostList),
                                                    eventList=zabbix.events(session['userName'], session['userPassword'], hostList, datetime.timestamp(session['secondValue']), datetime.timestamp(session['firstValue'])),
                                                    date=reportRange.getActualDateFormated())

        response = make_response(render_pdf(HTML(string=html), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')]))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename='+ '{}_events_{}.pdf'.format(zabbix.hostById(session['userName'], session['userPassword'], hostList).replace("/","-").replace(" ",""), reportRange.getActualDateFormated())                                                      
        return response

#Graphs Form
@app.route("/monitoring/graph-form")
def pageGraphForm():
    return render_template('graph-form.html', title="Graph Report",
                                              name="Graph Report",
                                              hostgroupList=zabbix.jsonAllHostgroups(session['userName'], session['userPassword']))

#Graphs Report (HTML)
@app.route("/monitoring/graph-report", methods=["GET", "POST"])
def pageGraphReport():
    if not os.path.exists("{}/static/images/temp/{}".format(parser.get("Reports", "graphs_image_temp_path"), session["userName"].replace(".", "_"))):
        os.mkdir("{}/static/images/temp/{}".format(parser.get("Reports", "graphs_image_temp_path"), session["userName"].replace(".", "_")))
    else:
        shutil.rmtree("{}/static/images/temp/{}".format(parser.get("Reports", "graphs_image_temp_path"), session["userName"].replace(".", "_")))
    reportRange = graphTimestamp.ReportRange()
    typeObj = reportRange.rangeModel()
    hostId = request.form["selectHost"]
    try:
        if request.form["selectStandard"]:
            formValue = request.form["selectStandard"]
            firstValue = typeObj[formValue][0]
            secondValue = typeObj[formValue][1]
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    except:
        if request.form["startDate"] and request.form["endDate"]:
            firstValue = datetime.strptime(request.form["startDate"]+' 00:00:00', '%Y-%m-%d %H:%M:%S')
            secondValue = datetime.strptime(request.form["endDate"]+' 23:59:59', '%Y-%m-%d %H:%M:%S')
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    return render_template("graph-report.html",
    title="Graph Report",
    name=zabbix.hostById(session["userName"], session["userPassword"], hostId),
    graphList=zabbix.graphs(session["userName"], session["userPassword"], hostId, firstValue, secondValue))

#Graphs Report (PDF)
@app.route('/monitoring/graph-report-pdf', methods=["GET", "POST"])
def pagePdfGraphsReport():
    if not os.path.exists("{}/static/images/temp/{}".format(parser.get("Reports", "graphs_image_temp_path"), session["userName"].replace(".", "_"))):
        os.mkdir("{}/static/images/temp/{}".format(parser.get("Reports", "graphs_image_temp_path"), session["userName"].replace(".", "_")))
    else:
        shutil.rmtree("{}/static/images/temp/{}".format(parser.get("Reports", "graphs_image_temp_path"), session["userName"].replace(".", "_")))
    reportRange = graphTimestamp.ReportRange()
    typeObj = reportRange.rangeModel()
    hostId = request.form["selectHost"]
    try:
        if request.form["selectStandard"]:
            formValue = request.form["selectStandard"]
            firstValue = typeObj[formValue][0]
            secondValue = typeObj[formValue][1]
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    except:
        if request.form["startDate"] and request.form["endDate"]:
            firstValue = datetime.strptime(request.form["startDate"]+' 00:00:00', '%Y-%m-%d %H:%M:%S')
            secondValue = datetime.strptime(request.form["endDate"]+' 23:59:59', '%Y-%m-%d %H:%M:%S')
            session['firstValue'] = firstValue
            session['secondValue'] = secondValue
    html = render_template('pdf-graph-report.html', 
    title="Graph Report", 
    name=zabbix.hostById(session["userName"], session["userPassword"], hostId),
    graphList=zabbix.graphs(session["userName"], session["userPassword"], hostId, firstValue, secondValue),
    date=reportRange.getActualDateFormated())

    response = make_response(render_pdf(HTML(string=html, base_url="/home/bruno.martins/Documents/Service IT/Projects/ITRC - Local"), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')]))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename='+ '{}_graphs_{}.pdf'.format(zabbix.hostById(session["userName"], session["userPassword"], hostId).replace("/","-").replace(" ",""), reportRange.getActualDateFormated())                                                      
    return response

#Host Form
@app.route("/monitoring/host-form")
def pageHostForm():
    return render_template("host-form.html", 
    title = "Host Report",
    name = "Host Report",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]))

#Host Report (HTML)
@app.route("/monitoring/host-report", methods=["GET", "POST"])
def pageHostReport():
    hostgroupId = request.form["selectHostgroup"]
    return render_template("host-report.html",
    title="Host Report",
    name=zabbix.hostgroupById(session["userName"], session["userPassword"], hostgroupId),
    identification=hostgroupId,
    hostList=zabbix.hosts(session["userName"], session["userPassword"], hostgroupId))

#Host Report (PDF)
@app.route('/monitoring/host-report-pdf', methods=["GET", "POST"])
def pagePdfHostsReport():
    reportRange = timestamp.ReportRange()
    hostgroupId = request.form["selectHostgroup"]
    html = render_template('pdf-host-report.html', 
    title="Hosts Report", 
    name=zabbix.hostgroupById(session['userName'], session['userPassword'], hostgroupId),
    hostList=zabbix.hosts(session['userName'], session['userPassword'], hostgroupId),
    date=reportRange.getActualDateFormated())

    response = make_response(render_pdf(HTML(string=html), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')]))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename='+ '{}_hosts_{}.pdf'.format(zabbix.hostgroupById(session['userName'], session['userPassword'], hostgroupId).replace("/","-").replace(" ",""), reportRange.getActualDateFormated())                                                      
    return response

#Hostgroup Form
@app.route("/monitoring/hostgroup-form")
def pageHostgroupForm():
    return render_template("hostgroup-form.html", 
    title = "Hostgroup Report",
    name = "Hostgroup Report",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]))

#Hostgroup Report (HTML)
@app.route("/monitoring/hostgroup-report", methods=["GET", "POST"])
def pageHostgroupReport():
    hostgroupList = request.form.getlist("selectHostgroup")
    array = []
    for hostgroup in hostgroupList:
        data = {}
        data["name"] = zabbix.hostgroupById(session["userName"], session["userPassword"], hostgroup)
        data["hostsList"] = zabbix.hostgroups(session["userName"], session["userPassword"], hostgroup)
        array.append(data)
    return render_template("hostgroup-report.html", title="Hostgroup Report",
                                                    list=array)

#Hostgroup Report (Excel)
@app.route("/monitoring/hostgroup-report-excel", methods=["GET", "POST"])
def excelHostgroupReport():
    hostgroupList = request.form.getlist("selectHostgroup")
    array = []
    for hostgroup in hostgroupList:
        data = {}
        data["name"] = zabbix.hostgroupById(session["userName"], session["userPassword"], hostgroup)
        data["hostsList"] = zabbix.hostgroups(session["userName"], session["userPassword"], hostgroup)
        array.append(data)
    file = excel.hostgroup(array)
    filename = "hostgroup-report.xls"
    file.save("temp/{}".format(filename))
    path = "temp/{}".format(filename)
    return send_file(path, as_attachment=True)

#Items Form
@app.route("/monitoring/item-form")
def pageItemForm():
    return render_template("item-form.html", 
    title = "Item Report",
    name = "Item Report",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]))

#Items Report (HTML)
@app.route("/monitoring/item-report", methods=["GET", "POST"])
def pageItemReport():
    hostList = request.form.getlist("selectHost")
    application = request.form.get("selectApllications")
    array = []
    for host in hostList:
        data = {}
        data["name"] = zabbix.hostById(session["userName"], session["userPassword"], host)
        data["itemList"] = zabbix.items(session["userName"], session["userPassword"], host, application)
        data["applicationFilter"] = application
        data["applicationList"] = zabbix.jsonAllApplicationsInHost(session["userName"], session["userPassword"], host)
        array.append(data)
    return render_template("item-report.html", title="Item Report",
                                               list=array,
                                               applicationFilter=application)

#Items Report (PDF)
@app.route('/monitoring/item-report-pdf', methods=["GET", "POST"])
def pagePdfItemReport():
    reportRange = timestamp.ReportRange()
    date = reportRange.getActualDateFormated()
    application = request.form.get("selectApllications")
    hostgroup = request.form.get("selectHostgroup")
    hostId = request.form.getlist("selectHost")
    userFolder = f"{session['userName']} - (items)"
    
    graphs_image_temp_path = parser.get("Reports", "graphs_image_temp_path")
    fullPath = f"{graphs_image_temp_path}/temp/{userFolder}"
    hostgroupName = zabbix.hostgroupById(session['userName'], session['userPassword'], hostgroup)
    if len(hostId) >= 2:
        if not os.path.exists(fullPath):
            os.mkdir(fullPath)
        else:
            shutil.rmtree(fullPath)
            os.mkdir(fullPath)
        for element in hostId:
            hostname = zabbix.hostById(session['userName'], session['userPassword'], element)
            jsonInformations = zabbix.items(session['userName'], session['userPassword'], element, application)
            html = render_template("pdf-item-report.html",
                                    title="Items Report",
                                    name=hostname,
                                    itemList=jsonInformations,
                                    applicationList=zabbix.jsonAllApplicationsInHost(session["userName"], session["userPassword"], element),
                                    applicationFilter=application,
                                    date=reportRange.getActualDateFormated())
            HTML(file_obj=html).write_pdf("{}/{} - (ITEMS).pdf".format(fullPath, fileFormater.modifyHostgroupName(hostname)), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')])
        filePaths = []
        for root, directories, files in os.walk(fullPath):
            for filename in files:
                filePath = os.path.join(root, filename)
                filePaths.append(filePath)
        zip_file = zipfile.ZipFile(f"temp/{userFolder}/{fileFormater.modifyHostgroupName(hostgroupName)}.zip", "w")
        with zip_file:
            for archive in filePaths:
                zip_file.write(archive)
        zip_file.close()
        return send_file(f"temp/{userFolder}/{fileFormater.modifyHostgroupName(hostgroupName)}.zip", as_attachment=True)
    else:
        html = render_template('pdf-item-report.html', 
        title="Items Report", 
        name=zabbix.hostById(session['userName'], session['userPassword'], hostId),
        itemList=zabbix.items(session['userName'], session['userPassword'], hostId, application), 
        applicationList=zabbix.jsonAllApplicationsInHost(session["userName"], session["userPassword"], hostId),
        applicationFilter=application,
        date=reportRange.getActualDateFormated())

        response = make_response(render_pdf(HTML(string=html), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')]))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename='+ '{}_items_{}.pdf'.format(zabbix.hostById(session['userName'], session['userPassword'], hostId).replace("/","-").replace(" ","").replace(".", "_"), reportRange.getActualDateFormated())                                                      
        return response

#Triggers Form
@app.route("/monitoring/trigger-form")
def pageTriggerForm():
    return render_template("trigger-form.html", 
    title = "Trigger Report",
    name = "Trigger Report",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]))

#Trigger Report (HTML)
@app.route("/monitoring/trigger-report", methods=["GET", "POST"])
def pageTriggerReport():
    tag = request.form.get("selectTags")
    hostList = request.form.getlist("selectHost")
    array = []
    for host in hostList:
        data = {}
        data['name'] = zabbix.hostById(session["userName"], session["userPassword"], host)
        data['infos'] = zabbix.jsonAllTriggersInHost(session["userName"], session["userPassword"], host, tag)
        array.append(data)
    return render_template("trigger-report.html", title="Trigger Report",
                                                  list=array)

#Trigger Report (PDF)
@app.route("/monitoring/trigger-report-pdf", methods=["GET", "POST"])
def pagePdfTriggerReport():
    reportRange = timestamp.ReportRange()
    date = reportRange.getActualDateFormated()
    tag = request.form.get("selectTags")
    hostgroup = request.form.get("selectHostgroup")
    hostid = request.form.getlist("selectHost")
    userFolder = f"{session['userName']} - (triggers)"

    graphs_image_temp_path = parser.get("Reports", "graphs_image_temp_path")
    fullPath = f"{graphs_image_temp_path}/temp/{userFolder}"
    hostgroupName = zabbix.hostgroupById(session['userName'], session['userPassword'], hostgroup)
    if len(hostid) >= 2:
        if not os.path.exists(fullPath):
            os.mkdir(fullPath)
        else:
            shutil.rmtree(fullPath)
            os.mkdir(fullPath)
        for element in hostid:
            hostname = zabbix.hostById(session['userName'], session['userPassword'], element)
            jsonInformations = zabbix.jsonAllTriggersInHost(session['userName'], session['userPassword'], element, tag)
            html = render_template("pdf-trigger-report.html",
                                       title="Triggers Report",
                                       name=hostname,
                                       triggerList=jsonInformations)
            HTML(file_obj=html).write_pdf("{}/{} - (TRIGGERS).pdf".format(fullPath, fileFormater.modifyHostgroupName(hostname)), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')])
        filePaths = []
        for root, directories, files in os.walk(fullPath):
            for filename in files:
                filePath = os.path.join(root, filename)
                filePaths.append(filePath)
        zip_file = zipfile.ZipFile(f"temp/{userFolder}/{fileFormater.modifyHostgroupName(hostgroupName)}.zip", "w")
        with zip_file:
            for file in filePaths:
                zip_file.write(file)
        zip_file.close()
        return send_file(f"temp/{userFolder}/{fileFormater.modifyHostgroupName(hostgroupName)}.zip", as_attachment=True)
    else:
        html = render_template('pdf-trigger-report.html', 
        title="Triggers Report", 
        name=zabbix.hostById(session['userName'], session['userPassword'], hostid),
        triggerList=zabbix.jsonAllTriggersInHost(session['userName'], session['userPassword'], hostid, tag),
        date=date)

        response = make_response(render_pdf(HTML(string=html), stylesheets=[CSS('./static/css/bootstrap.css'), CSS('./static/css/main.css')]))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename='+ '{}_triggers_{}.pdf'.format(zabbix.hostById(session['userName'], session['userPassword'], hostid).replace("/","-").replace(" ","").replace(".", "_ "), reportRange.getActualDateFormated())                                                      
        return response

#-----------------------------------------------------------------------------------#
#-----------------------------------Troubleshoot------------------------------------#
#-----------------------------------------------------------------------------------#
#Unsupported Items
@app.route("/troubleshoot/unsupported-items-form")
def pageUnsupportedItemsForm():
    return render_template("unsupported-items-form.html", 
    title = "Unsupported Items",
    name = "Unsupported Items",
    hostgroupList = zabbix.jsonAllHostgroups(session["userName"], session["userPassword"]))

#Unsupported Items (Excel)
@app.route("/troubleshoot/unsupported-items-excel", methods=["GET", "POST"])
def excelUnsupportedItems():
    hostgroupid = request.form["selectHostgroup"]
    listUnsupportedItems = zabbix.unsuportedItems(session["userName"], session["userPassword"], hostgroupid)
    file = excel.unsuportedItems(zabbix.hostgroupById(session["userName"], session["userPassword"], hostgroupid), listUnsupportedItems)
    filename = "{}-unsupported-items.xls".format(zabbix.hostgroupById(session["userName"], session["userPassword"], hostgroupid).replace("/", "-"))
    file.save("temp/{}".format(filename))
    path = "temp/{}".format(filename)
    return send_file(path, as_attachment=True)

#-----------------------------------------------------------------------------------#                                       
#--------------------------------JSON Routing System--------------------------------#        
#-----------------------------------------------------------------------------------#
#JSON: All hosts in hostgroup 
@app.route("/js-request/hosts-by-hostgroup/<hostgroupId>")
def jsonAllHostsInHostgroup(hostgroupId):
    listHosts = zabbix.jsonAllHosts(session['userName'], session['userPassword'], hostgroupId)
    return jsonify ({'hosts': listHosts})

@app.route("/js-request/tags-by-trigger/<hostId>")
def jsonAllTagsInTrigger(hostId):
    tagList = zabbix.jsonAllTagsInHost(session['userName'], session['userPassword'], hostId)
    return jsonify ({"tags":tagList})

@app.route("/js-request/applications-by-item/<hostid>")
def jsonAllApplicationsInHost(hostid):
    applicationList = zabbix.jsonAllApplicationsInHost(session['userName'], session['userPassword'], hostid)
    return jsonify ({"applications":applicationList})

@app.route("/js-request/triggers-by-hostgroup/<hostgroupid>")
def jsonAllTriggersInHostgroup(hostgroupid):
    triggerList = zabbix.jsonAllTriggersInHostgroup(session['userName'], session['userPassword'], hostgroupid)
    return jsonify({"triggers": triggerList})

@app.route("/testeJson")
def jsonTeste():
    lista = zabbix.availabilityAnalysis(session["userName"], 
                                        session["userPassword"], 
                                        778, 
                                        "Unavailable by ICMP", 
                                        1585709940.0, 
                                        1583031600.0)
    return jsonify({"teste": lista})

#-----------------------------------------------------------------------------------#
#---------------------------------Main Constructor----------------------------------#
#-----------------------------------------------------------------------------------#
if __name__ == '__main__':
    app.secret_key = parser.get("Flask", "secret_key")
    app.run('0.0.0.0', 
            parser.get("Flask", "port"), 
            threaded=parser.get("Flask", "threaded"), 
            debug=parser.get("Flask", "debug"))