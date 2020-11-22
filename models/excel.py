import xlwt

def unsuportedItems(excelName, unsuportedItemsList):
    #Main sheet
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(excelName[0:29].replace("/", "-"))
    titleStyle = xlwt.easyxf("font: bold 1;" "alignment: horizontal center;")
    elementStyle = xlwt.easyxf("alignment: horizontal center;")
    worksheet.write(0, 0, "Hostname", titleStyle)
    worksheet.col(0).width = 256 * 80
    worksheet.write(0, 1, "Nº of items", titleStyle)
    worksheet.col(1).width = 256 * 13
    worksheet.write(0, 2, "Total hosts", titleStyle)
    worksheet.col(2).width = 256 * 13
    worksheet.write(1, 2, len(unsuportedItemsList), titleStyle)

    #Counts - Main Column
    countHost = 0
    firstLine = 1
    columnHost = 0
    columnQuantity = 1

    #Counts = Hosts Sheets
    columnItemName = 0
    columnItemError = 1
    
    for i in unsuportedItemsList:
        worksheet.write(firstLine, columnHost, unsuportedItemsList[countHost]["host"])
        worksheet.write(firstLine, columnQuantity, unsuportedItemsList[countHost]["unsupportedItemsQtd"], elementStyle)
        if unsuportedItemsList[countHost]["unsupportedItemsQtd"] >= 1:
            itemLine = 1
            itemCount = 0
            worksheetItem = workbook.add_sheet("Line {}".format(str(firstLine+1)))
            worksheetItem.write(0, 0, "Item name", titleStyle)
            worksheetItem.col(0).width = 256 * 70
            worksheetItem.write(0, 1, "Description of Error", titleStyle)
            worksheetItem.col(1).width = 256 * 60
            for i in unsuportedItemsList[countHost]["unsupportedItemsList"]:
                worksheetItem.write(itemLine, columnItemName, unsuportedItemsList[countHost]["unsupportedItemsList"][itemCount]["itemName"])
                worksheetItem.write(itemLine, columnItemError, unsuportedItemsList[countHost]["unsupportedItemsList"][itemCount]["itemError"]) 
                itemLine += 1
                itemCount += 1
        countHost += 1
        firstLine += 1
    return workbook

def availabilityAnalysis(excelName, hostList, SLA):
    workbook = xlwt.Workbook()
    titleStyle = xlwt.easyxf("font: bold 1;" "alignment: horizontal center;") 
    #Main sheet - Triggers
    triggerWorksheet = workbook.add_sheet("Triggers")
    triggerWorksheet.write(0, 0, "Host", titleStyle)
    triggerWorksheet.col(0).width = 256 * 80
    triggerWorksheet.write(0, 1, "Trigger name", titleStyle)
    triggerWorksheet.col(1).width = 256 * 35
    triggerWorksheet.write(0, 2, "Problems", titleStyle)
    triggerWorksheet.col(2).width = 256 * 15
    triggerWorksheet.write(0, 3, "Ok", titleStyle)
    triggerWorksheet.col(3).width = 256 * 15

    #Second sheet - Events
    eventWorksheet = workbook.add_sheet("Events")
    eventWorksheet.write(0, 0, "Host", titleStyle)
    eventWorksheet.col(0).width = 256 * 80
    eventWorksheet.write(0, 1, "Trigger name", titleStyle)
    eventWorksheet.col(1).width = 256 * 35
    eventWorksheet.write(0, 2, "Problem time", titleStyle)
    eventWorksheet.col(2).width = 256 * 20
    eventWorksheet.write(0, 3, "Normalization time", titleStyle)
    eventWorksheet.col(3).width = 256 * 20
    eventWorksheet.write(0, 4, "SLA", titleStyle)
    eventWorksheet.col(4).width = 256 * 15

    #Line count (Trigger and Events sheets)
    triggerLine = 1
    eventLine = 1

    for i in hostList:
        if i.get("trigger"):
            triggerWorksheet.write(triggerLine, 0, i.get("hostname"))
            triggerWorksheet.write(triggerLine, 1, i.get("trigger"))
            triggerWorksheet.write(triggerLine, 2, i.get("problem"))
            triggerWorksheet.write(triggerLine, 3, i.get("ok"))
            if i.get("events"):
                for event in i.get("events"):
                    eventWorksheet.write(eventLine, 0, i.get("hostname"))
                    eventWorksheet.write(eventLine, 1, event.get("name"))
                    eventWorksheet.write(eventLine, 2, event.get("problemTime"))
                    eventWorksheet.write(eventLine, 3, event.get("okTime"))
                    eventWorksheet.write(eventLine, 4, event.get("sla"))
                    eventLine += 1
            triggerLine += 1
        else:
            pass
    triggerWorksheet.write(triggerLine, 2, "Average SLA", titleStyle)
    triggerWorksheet.write(triggerLine, 3, SLA, titleStyle)
    
    return workbook

def userList(excelName, userList):
    #Main sheet
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(excelName[0:29].replace("/", "-"))
    titleStyle = xlwt.easyxf("font: bold 1;" "alignment: horizontal center;")
    elementStyle = xlwt.easyxf("alignment: horizontal center;")
    worksheet.write(0, 0, "ID", titleStyle)
    worksheet.col(0).width = 256 * 7
    worksheet.write(0, 1, "Name", titleStyle)
    worksheet.col(1).width = 256 * 30
    worksheet.write(0, 2, "Surname", titleStyle)
    worksheet.col(2).width = 256 * 30
    worksheet.write(0, 3, "Alias", titleStyle)
    worksheet.col(3).width = 256 * 35
    worksheet.write(0, 4, "Type", titleStyle)
    worksheet.col(4).width = 256 * 18

    #Counts - Main Column
    countUser = 0
    firstLine = 1
    columnId = 0
    columnName = 1
    columnSurname = 2
    columnAlias = 3
    columnType = 4
    
    for i in userList:
        worksheet.write(firstLine, columnId, i["id"], elementStyle)
        worksheet.write(firstLine, columnName, i["name"], elementStyle)
        worksheet.write(firstLine, columnSurname, i["surname"], elementStyle)
        worksheet.write(firstLine, columnAlias, i["alias"], elementStyle)
        worksheet.write(firstLine, columnType, i["type"], elementStyle)
        firstLine += 1
    return workbook

def hostgroup(hostgroupList):
    #Main sheet
    workbook = xlwt.Workbook()
    for hostgroup in hostgroupList:
        worksheet = workbook.add_sheet(hostgroup.get("name")[0:29].replace("/", "-"))
        titleStyle = xlwt.easyxf("font: bold 1;" "alignment: horizontal center;")
        elementStyle = xlwt.easyxf("alignment: horizontal center;")
        worksheet.write(0, 0, "Name", titleStyle)
        worksheet.col(0).width = 256 * 7

        #Counts - Main Column
        countUser = 0
        firstLine = 1
        columnId = 0
        columnName = 1
        columnSurname = 2
        columnAlias = 3
        columnType = 4
        
        for i in hostgroup.get("hostsList"):
            worksheet.write(firstLine, columnId, i["name"], elementStyle)
            firstLine += 1
    return workbook