import matplotlib.pyplot as plt
from collections import defaultdict
import datetime
import time
import json
import requests
import numpy
import random
import PyQt5
from lcls_tools.devices.scLinac import LINAC_OBJECTS

global resultsFB, resultsIntlk, resultsRfRdy, startTime, endTime
resultsFB={} 
resultsIntlk={} 
resultsRfRdy={}
startTime=0
endTime=0

ARCHIVER_URL_FORMATTER = "http://{MACHINE}-archapp.slac.stanford.edu/retrieval/data/{{SUFFIX}}"
SINGLE_RESULT_SUFFIX = "getDataAtTime?at={TIME}-07:00&includeProxies=true"
RANGE_RESULT_SUFFIX = "getData.json"
TIMEOUT = 3

def makList():
    #################
    # this function generates a PV list for cavities
    # in SC linac
    #################

    pvList = []
    for lo in LINAC_OJECTS:
        for cm in lo.cryomodules:
            for cav in lo.cryomodules[cm].cavities:
                pvList.append(lo.cryomodules[cm].cavities[cav].pvPrefix)
    return pvList;



class Archiver(object):


    def __init__(self, machine):
        # type: (str) -> None
        self.url_formatter = ARCHIVER_URL_FORMATTER.format(MACHINE=machine)
        
        #******************************************************

#******************************************************

    def getValuesOverTimeRange(self, strtTim, endTim, timeInterval=None):
 #       # type: (List[str], datetime, datetime, int) -> Dict[str, Dict[str, List[Union[datetime, str]]]]
        global resultsFB, resultsIntlk, resultsRfRdy, startTime, endTime
        pvList=[]
        cavPvRfRdy={}
        cavPvFB={}
        cavPvIntlk={}

        #global cavPvFB, cavPvIntlk, cavPvRfRdy
        if (resultsFB == {}) or (strtTim != (time.mktime(datetime.datetime.startTime(strtTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))) or (endTime != int(time.mktime(datetime.datetime.strptime(endTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))):
            startTime = (time.mktime(datetime.datetime.startTime(strtTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))
            endTime = int(time.mktime(datetime.datetime.strptime(endTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))
            cavPv=makList()
            codeFlt = ["FB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
            for pv in cavPv:
                    cavPvFB.append(str(pv)+codeFlt[0])
                    cavPvIntlk.append(str(pv)+codeFlt[1])
                    cavPvRfRdy.append(str(pv)+codeFlt[2])
            for pv in cavPv:
                for i in range(3):
                    pvList.append(str(pv) + codeFlt[i])
            
            url = self.url_formatter.format(SUFFIX=RANGE_RESULT_SUFFIX)

            for pv in pvList:
                       response = requests.get(url=url, timeout=TIMEOUT,
                                               params={"pv": pv,
                                                       "from": strtTim.isoformat() + "-07:00",
                                                       "to": endTim.isoformat() + "-07:00"})
                       results = {}
    
                       try:
                           jsonData = json.loads(response.text)
                           element = jsonData.pop()
                           result = {"times": [], "values": []}
                           for datum in element[u'data']:
                               result["times"].append(datum[u'secs'])
                               result["values"].append(datum[u'val'])
    
                           results[pv] = result["values"],result["times"]
    
    
                           for cav in cavPvFB:
                                resultsFB.append(results[cav])
                           for cav1 in cavPvIntlk:
                                resultsIntlk.append(results[cav1])
                           for cav2 in cavPvRfRdy:
                                resultsRfRdy.append(results[cav2])
    
                       except ValueError:
                           print("JSON error with {PVS}".format(PVS=pvList))
        else:
            return;
            


#******************************************************

def getValuesOverTimeDummy(strtTim, endTim, timeInterval=None):
    global resultsFB, resultsIntlk, resultsRfRdy, startTime, endTime
    results={}
    cavPvRfRdy=[]
    cavPvFB=[]
    cavPvIntlk=[]
    cavPv=[]
#    print(time.mktime(datetime.datetime.strptime(strtTim, '%m/%d/%Y %H:%M:%S' ).timetuple()), '=',startTime)
    if (resultsFB == {}) or (startTime != (time.mktime(datetime.datetime.strptime(strtTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))) \
        or (endTime != (time.mktime(datetime.datetime.strptime(endTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))):
        #print('oops.  fell through')
        startTime = int(time.mktime(datetime.datetime.strptime(strtTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))
        endTime = int(time.mktime(datetime.datetime.strptime(endTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))
             
        pvList=makList()
        codeFlt = ["FB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
        for pv in pvList:
            for i in range(3):
                cavPv.append(str(pv) + codeFlt[i])
        for avP in cavPv:
            result={"values":[], "times":[]}
            ranJe = numpy.random.randint(1,4)
            eventTime= (endTime-startTime)/ranJe
            for i in range(ranJe):
                 fltType = numpy.random.randint(0,6)
                 result["values"].append(2**fltType)
                 dt= random.randrange(startTime, endTime,ranJe)
#                 dt=i*eventTime+startTime
                 #posTimestamp=int((dt - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1))
                 result["times"].append(dt)
            results[avP]=result
        for pv in pvList:
            cavPvFB.append(str(pv)+codeFlt[0])
            cavPvIntlk.append(str(pv)+codeFlt[1])
            cavPvRfRdy.append(str(pv)+codeFlt[2])
        for cav in cavPvFB:
            resultsFB[cav]=results[cav]
        for cav1 in cavPvIntlk:
            resultsIntlk[cav1]=results[cav1]
        for cav2 in cavPvRfRdy:
            resultsRfRdy[cav2]=results[cav2]
    else:
        return;


#******************************************************
        
def cmFlts():
###
    #   cmFlts determines the sum of the number of cryomodule faults from the global 
    #  resultsFB, resultsIntlk, resultsRfRdy Dicts  which are generated by the archiver calls
    #  ReWrite complete
    
    b=[]
    c=[]
    total=[]
    totalLo = []
    totalHi=[]
    stDev=[]
    stDLo=[]
    stDHi=[]

    aaaa=list(resultsIntlk.keys())
#    print(aaaa)
    for n in range(0, 37):
        CMtot = []
        for i in range(0, 8):
             tut=aaaa[i+n*8]
    
             CMtot.append(len(resultsIntlk[tut]['values']))
        total.append(numpy.sum(CMtot))
        stDev.append(numpy.std(CMtot))
    
    for i in range(17):
            totalLo.append(total[i])
            stDLo.append(stDev[i])
            b.append(i + 1)
    for i in range(17, 37):
            totalHi.append(total[i])
            stDHi.append(stDev[i])
            c.append(i - 1)
    
    return b,c,totalLo, totalHi, stDLo, stDHi;
#****************************************************

#****************************************************
def sortStats(CavFlts, CavRdy):
    i=0
    n=0
    FltTime=[]
    dd=[]
    while i <= (len(CavFlts) - 1):
       Flt = CavFlts[i]
       Rdy =CavRdy[n]

       if (int(Rdy) >= int(Flt)) and ((i + 1) <= len(CavFlts)) and ((n + 1) <= len(CavRdy)):
           FltTime.append(int(Rdy) - int(Flt))
           while (int(Flt) <= int(Rdy)) and ((i + 1) <= len(CavFlts)):
              try:
                i += 1
                if (i + 1) <= len(CavFlts):
                   Flt = CavFlts[i]
                continue
              except IndexError:
                #print("incremented i too far")
                break

       elif (int(Flt) >= int(Rdy)) and ((n + 1) < len(CavRdy)):
           try:
              while (Flt >= Rdy):
                n += 1
                Rdy = CavRdy[n]
                continue
           except IndexError:
              #print("incremented n too far")
              break
       else:
           break
    if cavFaults==[]:
       FltTime=0

    return FltTime;
#***************************************************

#***************************************************
def CmStats():
    global resultsIntlk, resultsRfRdy
    b=[]
    c=[]
    dd=[]
    cavTot =[]
    CMtot=[]
    total=[]
    totalLo = []
    totalHi=[]
    average=[]
    stDev=[]
    stDLo=[]
    stDHi=[]
    
    pvList = makList()
    codeFlt = ["FB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
    for pv in pvList:
        CavFltDat= (resultsIntlk[(str(pv)+ codeFlt[1])]['times'])
        CavRdyDat= (resultsRfRdy[(str(pv)+ codeFlt[2])]['times'])
#get the recover times for a single cavity
        dd=[]
        dd=sortStats(CavFltDat,CavRdyDat)
        #print dd
        xx = numpy.array(dd)
        # set division factor for appropriate unit of time; hours, min, or sec
        cavTot.append(numpy.sum(xx)/60.0/60/60)
    
    #print(len(cavTot))
    for n in range(0,37):
        CMtot=[]
        for i in range(0,8):
            indCav = i + n*8.0
            CMtot.append(cavTot[int(indCav)])
        total.append(numpy.sum(CMtot))
        average.append(numpy.mean(CMtot))
        stDev.append(numpy.std(CMtot))
#    print(total)
    for i in range(17):
        totalLo.append(average[i])
        stDLo.append(stDev[i])
        b.append(i+1)
    for i in range(17,37):
        totalHi.append(average[i])
        stDHi.append(stDev[i])
        c.append(i-1)
    return b,c,totalLo, totalHi, stDLo, stDHi;
#***************************************************

#***************************************************
def makCavPv(spinOut):
    pv2 = []
    pvL = ""
    cav = []
    # print(spinOut)
    if spinOut == "H1" or spinOut == "H2":
        pvL = "ACCL:L1B:" + spinOut
    else:
        if int(spinOut) == 1:
            pvL = "ACCL:L0B:0" + str(spinOut)
        if 1 < int(spinOut) < 4:
            pvL = "ACCL:L1B:0" + str(spinOut)
        if 3 < int(spinOut) < 10:
            pvL = "ACCL:L2B:0" + str(spinOut)
        if 9 < int(spinOut) < 16:
            pvL = "ACCL:L2B:" + str(spinOut)
        if 15 < int(spinOut) < 36:
            pvL = "ACCL:L3B:" + str(spinOut)
    for i in range(1, 9):
        alpha = pvL + str(i) + "0"
        # print(alpha)
        pv2.append(alpha)
        if len(str(spinOut)) == 1:
            cav.append("0"+str(spinOut) + "-" + str(i) + "0")
        else:
            cav.append(str(spinOut)+"-"+str(i)+"0")
    if str(spinOut) == "Not":
        pv2 = "NaN"
    return pv2, cav;
#***********************************************
#
#
def cavDatCnt(caVs, sT, fiN):
    results={}
    if caVs != "NaN":
        # cavPv = []
        # reFbSults=[]
        # reIntlkSults = []
        # codeFlt = ["0:FB_SUM", "0:RFS:INTLK_FIRST", "0:RFREADYFORBEAM"]
        # for pv in pvLow:
        #    for i in range(2):
        #        cavPv.append(str(pv) + codeFlt[i])
        #    result = archiver.getValuesOverTimeRange(cavPv[0], sT, fiN)
        #    result2 = archiver.getValuesOverTimeRange(cavPv[1], sT, fiN)
        for pv in caVs:

            #
            #  bozo and clwn are variables to count the number for each type of fault in the dataset
            #  fault code '1' is PLL lock, '2' is ioc watchdog, '4' is the Interlock Fault summary, '8' is Comm fault
            #  '16' is an SSA fault and '32 is a cavity quench
            #
            pvL=pv+':RFS:INTLK_FIRST'
            pvFB = pv+":FB_SUM"
            #print(pvL, resultsIntlk.keys())
            bozo = {"PLLlock": [], "iocDog": [], "IntlkFlt": [], "CommFlt": [], "SSAFlt": [],
                    "Quench": [], "Clips": []}
            clwn = []
            clwn = resultsIntlk[pvL]['values']  # read 'values' into clwn list
            #print(clwn)
            bozo["PLLlock"] = clwn.count(1)
            bozo["iocDog"] = clwn.count(2)
            bozo["IntlkFlt"] = clwn.count(4)
            bozo["CommFlt"] = clwn.count(8)
            bozo["SSAFlt"] = clwn.count(16)
            bozo["Quench"] = clwn.count(32)
            bozo["Clips"] = len(resultsFB[pvFB]["values"])
            results[pvL] = bozo
    else:
        results = []
    return results;
#
#***********************************************
def cavFaults(cmUpper, cmLower, Start, End):
    if cmUpper != "Not":
        pvCav, cavU = makCavPv(cmUpper)
        resP = cavDatCnt(pvCav,Start, End)
#        print(resP)
    else:
        cavU = []
        resP=[]
    if  cmLower != "Not":
        pvCav, cavL =makCavPv(cmLower)
        resP2 = cavDatCnt(pvCav, Start, End)
    else:
        cavL=[]
        resP2=[]
    return cavU, cavL, resP, resP2;
#******************************************************
#
def cavStatCnt(Cav, Start, End):
     cc="00"
     dd=[]
     xx=[]
     cavAve=[]
     cavStD=[]
     results={}
     results2 ={}
     ##################
    #  The commented out block calls the archiver for the interlock and clipping faults
    #############
    #cavPv = []
    #reFbSults=[]
    #reIntlkSults = []
    #codeFlt = ["0:FB_SUM", "0:RFS:INTLK_FIRST", "0:RFREADYFORBEAM"]
    #for ca in Cav:
    #    for i in range(2):
    #        cavPv.append(str(Cav) + codeFlt[i])
    #    result = archiver.getValuesOverTimeRange(cavPv[0], Start, End)
    #    result2 = archiver.getValuesOverTimeRange(cavPv[1], Start, End)
    #############

     for ca in Cav:
        caP = ca +":RFS:INTLK_FIRST"
        caR = ca + ":RFREADYFORBEAM"
#        print(ca)
#        result={ca:{"times":[]}}
#        result2 = {ca:{"times": []}}
#        for i in range(random.randint(1,15)):
#             result["times"].append(random.randint(9500,10000))
#             result2["times"].append(random.randint(9500, 10000))
#        results[ca]=sorted(result["times"])  #this is the time of the faults
#        results2[ca]=sorted(result2["times"])  # this is the time that rf shows fully recovered
        
        results[ca]=sorted(resultsIntlk[caP]["times"])  #this is the time of the faults
        results2[ca]=sorted(resultsRfRdy[caR]["times"])  # this is the time that rf shows fully recovered
#        print(ca,results[ca],results2[ca])
     aaaa = results.keys()
#     print(aaaa)
     for cav in aaaa:
        i = 0
        n = 0
        CavFltDat = (results[cav])  # get the flt times for a single cavity
        CavRdyDat = (results2[cav])  #get the recover times for a single cavity
        dd=[]
        dd=sortStats(CavFltDat,CavRdyDat)
        xx = numpy.array(dd)
        if len(xx) > 1:
            cavAve.append(numpy.mean(xx)/60.0)
            cavStD.append(numpy.std(xx)/60.0)
        elif len(xx) == 1:
            cavAve.append(xx[0]/60.0)
            cavStD.append(0)
        else:
            cavAve.append(0)
            cavStD.append(0)
        #print("cavAve=",cavAve,"cavStD=",cavStD)
     return cavAve, cavStD;
#**********************************************
#
#
#***********************************************
def cavStats(cmUpper,cmLower, Start, End):
     if cmUpper != "Not":
        pvCav, cavU = makCavPv(cmUpper)
#        print(pvCav)
        resPave, resPstd = cavStatCnt(pvCav,Start,End)
     else:
        cavU =[]
        resPave =[]
        resPstd =[]
     if cmLower != "Not":
        pvCav2, cavU2 = makCavPv(cmLower)
        resPave2, resPstd2 = cavStatCnt(pvCav2,Start,End)
     else:
         cavU2=[]
         resPave2 = []
         resPstd2 = []
     return cavU, cavU2, resPave, resPstd, resPave2, resPstd2;
 
def XfelDsply(strt):
    b=[]
    vTime=[]
    totalLo=[]
    totalHi=[]
    fltCount = {}

   # begin = datetime.date(strt.strftime('%Y,%m,%d'))
    begin= datetime.date(int(2021),int(7),int(22))
     
#    print(begin)
    aaaa=list(resultsIntlk.keys())
    for n in range(0, 37):
        CMtot = []
        mylist = []
        fltDay = {"day": [], "value": []}
        for i in range(0, 8):
             tut=aaaa[i+n*8]
#             print(tut)
             vTime= sorted( resultsIntlk[tut]['times'])
             for v in vTime:
                 b=(datetime.date.fromtimestamp(v))
#                 print(n,i,b)
                 daysCnt = b - begin
#                 CMtot.append(datetime.datetime.strftime(b, '%d'))
                 CMtot.append(int(daysCnt.days))

                 mylist = list(dict.fromkeys(CMtot))
        mylist.sort()
        for CMc in mylist:
             fltDay["day"].append(int(CMc))
             fltDay["value"].append(CMtot.count(str(CMc)))   
        fltCount[n] = fltDay["day"],fltDay["value"]
#        for i in range(17):
#           totalLo.append(fltCount[i])
#        for i in range(17,37):
#           totalHi.append(fltCount[i])
        
    return (fltCount)
    

    

#    dailyFlts = resultsIntlk


if __name__ == "__main__":
    archiver = Archiver("lcls")
    startDate = datetime.datetime.now()
#    startTime = int(time.mktime(datetime.datetime.strptime(startDate, '%m/%d/%Y %H:%M:%S' ).timetuple()))
    startTime = startDate.strftime('%m/%d/%Y %H:%M:%S') 
    #print(startDate, startTime)
    endDate = startDate + datetime.timedelta(days=50)
    endTime = endDate.strftime('%m/%d/%Y %H:%M:%S')
    getValuesOverTimeDummy(startTime, endTime)
    cmNumb=[]
    days=[]
    zzz=[]
    totalLo=[]
    totalHi=[]
    #print(matplotlib.__version__, numpy.__version__)
    #e,f,DisLow,DisHi, DisLoStd, DisHiStd = CmStats(datetime.time,datetime.time)
    #print "e=", e  , "\n\r", "DisLow=", DisLow, "DisLoStd=",DisLoStd
    #e, f, r1,r2,r3,r4  = cavStats("4","27",startDate,endDate)
    #print ("e=",e,"r1=", r1, r2) 
    squid = XfelDsply(startDate)
    #print "e=", e, totLo, StDlo
    #e, f, r1,r2  = cavFaults("4","27",datetime.time,datetime.time)
    #print ("r1=", r1)
    #PyQt5.QtCore.QDateTime(2000, 1, 1, 0, 0) PyQt5.QtCore.QDateTime(2000, 1, 1, 0, 0)
           
    for i in range(17):
        days.append(squid[i][0])
        zzz.append(squid[i][1])
        for n in range(len(squid[i][0])):
            cmNumb.append(int(i))
    daysA=numpy.concatenate([numpy.array(i) for i in days])
    zzzA = numpy.concatenate([numpy.array(i) for i in zzz])
    plt.scatter(daysA,cmNumb, c=zzzA)
    plt.show()
    
    # for i in range(17, 37):
    #     totalHi.append(squid[i])
    # cmList=list(squid.keys())
    # for cm in cmList:
    #     days.append(squid[cm][0])
    #     zzz.append(squid[cm][1])
    #     for n in range(len(squid[cm][0])):
    #         cmNumb.append(int(cm))
        
    
    #plt.plot(squid['day'],squid[])
    

