from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ReportRange():
    def __init__(self):
        self.monthArray =  { 1: 31,
                             2: 28 if datetime.now().year // 4 else 29,
                             3: 31,
                             4: 30,
                             5: 31, 
                             6: 30,
                             7: 31,
                             8: 31, 
                             9: 30,
                             10: 31,
                             11: 30,
                             12: 31
                            }
        self.monthName = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio", 
            6: "Junho",
            7: "Julho",
            8: "Agosto", 
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro"
        }
    
    #--------------------------------------Formatter------------------------------------#
    def capacityTime(self, timestamp):
        actualDate = datetime.fromtimestamp(timestamp)
        return "{}/{} - {}:{}:{}".format(actualDate.day, actualDate.month, actualDate.hour, actualDate.minute, actualDate.second)

    def getActualDateFormated(self):
        actualDate = datetime.now()
        return "{}/{}/{} at {}:{}".format(actualDate.month, actualDate.day, actualDate.year, actualDate.hour, actualDate.minute)
    
    def rangeModel(self):
        model = {
        "today":[self.getBeginDay(), self.getEndDay()],
        "todaySoFar": [self.getBeginDay(), self.getActualDate()],
        "thisWeek": [self.getBeginWeekDay(), self.getEndingWeekDay()],
        "thisWeekSoFar": [self.getBeginWeekDay(), self.getActualDate()], 
        "thisMonth": [self.getBeginMonthDay(), self.getEndingMonthDay()],
        "thisMonthSoFar": [self.getBeginMonthDay(), self.getActualDate()], 
        "thisYear":[self.getBeginYearDay(), self.getLastYearDay()],
        "thisYearSoFar":[self.getBeginYearDay(), self.getActualDate()], 
        "yesterday":[self.getYesterdayBeginDay(), self.getYesterdayEndDay()],
        "dayBeforeYesterday": [self.getDayBeforeYesterdayBeginDay(), self.getDayBeforeYesterdayEndDay()],
        "thisDayLastWeek":[self.getThisDayLastWeekBeginDay(), self.getThisDayLastWeekEndDay()],
        "previousWeek":[self.previousWeekBeginWeek(), self.previousWeekEndWeek()],
        "previousMonth":[self.getPreviousMonthBeginMonth(), self.getPreviousMonthEndingMonth()],
        "previousYear": [self.getPreviousYearStartDay(), self.getPreviousYearLastDay()],
        "last5Minutes":[self.getLastMinutes(5), self.getActualDate()],
        "last15Minutes":[self.getLastMinutes(15), self.getActualDate()],
        "last30Minutes":[self.getLastMinutes(30), self.getActualDate()],
        "last1Hour":[self.getLastHours(1), self.getActualDate()],
        "last3Hours":[self.getLastHours(3), self.getActualDate()],
        "last6Hours":[self.getLastHours(6), self.getActualDate()],
        "last12Hours":[self.getLastHours(12), self.getActualDate()],
        "last1Day":[self.getLastDays(1), self.getActualDate()],
        "last2Days":[self.getLastDays(2), self.getActualDate()],
        "last7Days":[self.getLastDays(7), self.getActualDate()],
        "last30Days":[self.getLastDays(30), self.getActualDate()],
        "last3Months":[self.getLastDays(90), self.getActualDate()],
        "last6months":[self.getLastDays(180), self.getActualDate()],
        "lastYear":[self.getLastDays(365), self.getActualDate()],
        "last2Years":[self.getLastDays(730), self.getActualDate()]
        }
        return model
    
    #---------------------------------------Actual--------------------------------------#
    def getActualDate(self):
        return datetime.now()

    def getBeginDay(self):
        actualDate = datetime.now()
        return datetime(actualDate.year, actualDate.month, actualDate.day, 0, 0)

    def getEndDay(self):
        actualDate = datetime.now()
        return datetime(actualDate.year, actualDate.month, actualDate.day, 23, 59, 59)

    def getBeginWeekDay(self):
        beginWeekDay = datetime.now() - timedelta(days=datetime.today().weekday())
        return datetime(beginWeekDay.year, beginWeekDay.month, beginWeekDay.day, beginWeekDay.hour, beginWeekDay.minute)

    def getEndingWeekDay(self):
        endWeekDay = datetime.now() + timedelta(days=6 - datetime.today().weekday())
        return datetime(endWeekDay.year, endWeekDay.month, endWeekDay.day, endWeekDay.hour, endWeekDay.minute)

    def getBeginMonthDay(self):
        actualDate = datetime.now()
        return datetime(actualDate.year, actualDate.month, 1, 00, 00)

    def getEndingMonthDay(self):
        actualDate = datetime.now()
        return datetime(actualDate.year, actualDate.month, self.monthArray[actualDate.month], 23, 59)

    def getBeginYearDay(self):
        actualDate = datetime.now()
        return datetime(actualDate.year, 1, 1, 0, 0, 0)

    def getLastYearDay(self):
        actualDate = datetime.now()
        return datetime(actualDate.year, 12, 31, 23, 59, 59)

    #--------------------------------------Previous-------------------------------------#
    def getYesterdayBeginDay(self):
        yesterdayBeginDay = datetime.now() - timedelta(days=1)
        return datetime(yesterdayBeginDay.year, yesterdayBeginDay.month, yesterdayBeginDay.day, 00, 00)

    def getYesterdayEndDay(self):
        yesterdayEndDay = datetime.now() - timedelta(days=1)
        return datetime(yesterdayEndDay.year, yesterdayEndDay.month, yesterdayEndDay.day, 23, 59)

    def getDayBeforeYesterdayBeginDay(self):
        dayBeforeYesterday = datetime.now() - timedelta(days=2)
        return datetime(dayBeforeYesterday.year, dayBeforeYesterday.month, dayBeforeYesterday.day, 00, 00)

    def getDayBeforeYesterdayEndDay(self): 
        dayBeforeYesterday = datetime.now() - timedelta(days=2)
        return datetime(dayBeforeYesterday.year, dayBeforeYesterday.month, dayBeforeYesterday.day, 23, 59)

    def getThisDayLastWeekBeginDay(self):
        thisDayLastWeek = datetime.now() - timedelta(days=7)
        return datetime(thisDayLastWeek.year, thisDayLastWeek.month, thisDayLastWeek.day, 00, 00)

    def getThisDayLastWeekEndDay(self):
        thisDayLastWeek = datetime.now() - timedelta(days=7)
        return datetime(thisDayLastWeek.year, thisDayLastWeek.month, thisDayLastWeek.day, 23, 59)        

    def previousWeekBeginWeek(self):
        previousWeek = (datetime.now() - timedelta(days=datetime.today().weekday())) - timedelta(days=7)
        return datetime(previousWeek.year, previousWeek.month, previousWeek.day, 0, 0)

    def previousWeekEndWeek(self):
        previousWeek = (datetime.now() - timedelta(days=datetime.today().weekday())) - timedelta(days=1)
        return datetime(previousWeek.year, previousWeek.month, previousWeek.day, 23, 59)

    def getPreviousMonthBeginMonth(self):
        previewMonth = datetime.now() - relativedelta(months=1)
        return datetime(previewMonth.year, previewMonth.month, 1, 0, 0)

    def getPreviousMonthEndingMonth(self):
        previewMonth = datetime.now() - relativedelta(months=1)
        return datetime(previewMonth.year, previewMonth.month, self.monthArray[previewMonth.month], 23, 59)
        
    def getPreviousYearStartDay(self):
        actualDate = datetime.now()
        return datetime(actualDate.year-1, 1, 1, 00, 00, 00)

    def getPreviousYearLastDay(self):
        actualDate = datetime.now()
        return datetime(actualDate.year-1, 12, 31, 23, 59, 59)
    #---------------------------------------Last----------------------------------------#
    def getLastMinutes(self, minuteReport): #Can be 5, 15 or 30 minutes.
        lastMinutes = datetime.now() - timedelta(minutes=minuteReport)
        report = datetime(lastMinutes.year, lastMinutes.month, lastMinutes.day, lastMinutes.hour, lastMinutes.minute)
        return report

    def getLastHours(self, hourReport): #Can be 1, 3, 6 or 12 hours.
        lastHours = datetime.now() - timedelta(hours=hourReport)
        report = datetime(lastHours.year, lastHours.month, lastHours.day, lastHours.hour, lastHours.minute)
        return report

    def getLastDays(self, dayReport): #Can be 1, 2, 7 or 30, 60 days.
        lastDays = datetime.now() - timedelta(days=dayReport)
        report = datetime(lastDays.year, lastDays.month, lastDays.day, lastDays.hour, lastDays.minute)
        return report
    
    #---------------------------------------Books--------------------------------------#
    def getPreviousSixMonths(self):
        today = self.getActualDate()
        return [
            {"month": self.monthName[(today - relativedelta(months=6)).month], 
             
             "begin": datetime.timestamp(datetime((today - relativedelta(months=6)).year, 
                                                  (today - relativedelta(months=6)).month, 1, 00, 00)),
            
             "end": datetime.timestamp(datetime((today - relativedelta(months=6)).year, 
                                                (today - relativedelta(months=6)).month, 
                                                self.monthArray[(today - relativedelta(months=6)).month], 00, 00))},

            {"month": self.monthName[(today - relativedelta(months=5)).month], 
             
             "begin": datetime.timestamp(datetime((today - relativedelta(months=5)).year, 
                                                  (today - relativedelta(months=5)).month, 1, 00, 00)),
            
             "end": datetime.timestamp(datetime((today - relativedelta(months=5)).year, 
                                                (today - relativedelta(months=5)).month, 
                                                self.monthArray[(today - relativedelta(months=5)).month], 00, 00))},

            {"month": self.monthName[(today - relativedelta(months=4)).month], 
             
             "begin": datetime.timestamp(datetime((today - relativedelta(months=4)).year, 
                                                  (today - relativedelta(months=4)).month, 1, 00, 00)),
            
             "end": datetime.timestamp(datetime((today - relativedelta(months=4)).year, 
                                                (today - relativedelta(months=4)).month, 
                                                self.monthArray[(today - relativedelta(months=4)).month], 00, 00))},

            {"month": self.monthName[(today - relativedelta(months=3)).month], 
             
             "begin": datetime.timestamp(datetime((today - relativedelta(months=3)).year, 
                                                  (today - relativedelta(months=3)).month, 1, 00, 00)),
            
             "end": datetime.timestamp(datetime((today - relativedelta(months=3)).year, 
                                                (today - relativedelta(months=3)).month, 
                                                self.monthArray[(today - relativedelta(months=3)).month], 00, 00))},

            {"month": self.monthName[(today - relativedelta(months=2)).month], 
             
             "begin": datetime.timestamp(datetime((today - relativedelta(months=2)).year, 
                                                  (today - relativedelta(months=2)).month, 1, 00, 00)),
            
             "end": datetime.timestamp(datetime((today - relativedelta(months=2)).year, 
                                                (today - relativedelta(months=2)).month, 
                                                self.monthArray[(today - relativedelta(months=2)).month], 00, 00))},

            {"month": self.monthName[(today - relativedelta(months=1)).month], 
             
             "begin": datetime.timestamp(datetime((today - relativedelta(months=1)).year, 
                                                  (today - relativedelta(months=1)).month, 1, 00, 00)),
            
             "end": datetime.timestamp(datetime((today - relativedelta(months=1)).year, 
                                                (today - relativedelta(months=1)).month, 
                                                self.monthArray[(today - relativedelta(months=1)).month], 00, 00))}]