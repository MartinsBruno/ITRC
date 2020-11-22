from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ReportRange():
    #--------------------------------------Formatter------------------------------------#

    def getActualDateFormated(self):
        actualDate = datetime.now()
        return "{}/{}/{} at {}:{}".format(actualDate.month, actualDate.day, actualDate.year, actualDate.hour, actualDate.minute)
    
    def rangeModel(self):
        model = {
        #Actual
        "today":[self.getBeginDay(), self.getBeginDay()],
        "todaySoFar": [self.getBeginDay(), self.getActualDate()],
        "thisWeek": [self.getBeginWeekDay(), self.getBeginWeekDay()],
        "thisWeekSoFar": [self.getBeginWeekDay(), self.getActualDate()], 
        "thisMonth": [self.getBeginMonthDay(), self.getBeginMonthDay()],
        "thisMonthSoFar": [self.getBeginMonthDay(), self.getActualDate()], 
        "thisYear":[self.getBeginYearDay(), self.getBeginYearDay()],
        "thisYearSoFar":[self.getBeginYearDay(), self.getActualDate()],
        #Previous
        "yesterday":[self.getYesterdayBeginDay(), self.getYesterdayBeginDay()],
        "dayBeforeYesterday": [self.getDayBeforeYesterdayBeginDay(), self.getDayBeforeYesterdayBeginDay()],
        "thisDayLastWeek":[self.getThisDayLastWeekBeginDay(), self.getThisDayLastWeekBeginDay()],
        "previousWeek":[self.previousWeekBeginWeek(), self.previousWeekBeginWeek()],
        "previousMonth":[self.getPreviousMonthBeginMonth(), self.getPreviousMonthBeginMonth()],
        "previousYear": [self.getPreviousYearStartDay(), self.getPreviousYearStartDay()],
        #Last
        "last5Minutes":[self.getLastMinutes(5), self.getActualDate()],
        "last15Minutes":[self.getLastMinutes(15), self.getActualDate()],
        "last30Minutes":[self.getLastMinutes(30), self.getActualDate()],
        "last1Hour":[self.getLastHours(1), self.getActualDate()],
        "last3Hours":[self.getLastHours(3), self.getActualDate()],
        "last6Hours":[self.getLastHours(6), self.getActualDate()],
        "last12Hours":[self.getLastHours(12), self.getActualDate()],
        "last1Day":[self.getLastHours(24), self.getActualDate()],
        "last2Days":[self.getLastDays(2), self.getActualDate()],
        "last7Days":[self.getLastDays(7), self.getActualDate()],
        "last30Days":[self.getLastDays(30), self.getActualDate()],
        "last3Months":[self.getLastMonths(3), self.getActualDate()],
        "last6months":[self.getLastMonths(6), self.getActualDate()],
        "lastYear":[self.getLastYears(1), self.getActualDate()],
        "last2Years":[self.getLastYears(2), self.getActualDate()]
        }
        return model
    
    #---------------------------------------Actual--------------------------------------#
    def getActualDate(self):
        return "now"

    def getBeginDay(self):
        return "now/d"

    def getBeginWeekDay(self):
        return "now/w"

    def getBeginMonthDay(self):
        return "now/M"

    def getBeginYearDay(self):
        return "now/y"

    #--------------------------------------Previous-------------------------------------#
    def getYesterdayBeginDay(self):
        return "now-1d/d"

    def getDayBeforeYesterdayBeginDay(self):
        return "now-2d/d"

    def getThisDayLastWeekBeginDay(self):
        return "now-1w/d"     

    def previousWeekBeginWeek(self):
        return "now-1w/w"

    def getPreviousMonthBeginMonth(self):
        return "now-1M/M"

    def getPreviousYearStartDay(self):
        return "now-1y/y"
    #---------------------------------------Last----------------------------------------#
    def getLastMinutes(self, minute): #Can be 5, 15 or 30 minutes.
        return "now-{}m".format(minute)

    def getLastHours(self, hour): #Can be 1, 3, 6 or 12 hours.
        return "now-{}h".format(hour)

    def getLastDays(self, day): #Can be 1, 2, 7 or 30, 60 days.
        return "now-{}d".format(day)
    
    def getLastMonths(self, month): #Can be 3 or 6 months.
        return "now-{}M".format(month)
    
    def getLastYears(self, year): #Can be 3 or 6 months.
        return "now-{}y".format(year)