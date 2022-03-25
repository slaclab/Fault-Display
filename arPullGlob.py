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
from lcls_tools.data_analysis.archiver import Archiver, ArchiverData

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
    # this function generates a PV prefix list for cavities
    # in SC linac like 'ACCL:L0B:0110:'
    #################

    pvList = []
    for lo in LINAC_OBJECTS:
        for cm in lo.cryomodules:
            for cav in lo.cryomodules[cm].cavities:
                pvList.append(lo.cryomodules[cm].cavities[cav].pvPrefix)
    return pvList;


#******************************************************

def getValuesOverTimeRange(strtTim, endTim, timeInterval=None):
 #       # type: ( datetime, datetime, int) -> Dict[str, Dict[str, List[Union[datetime, str]]]]
##
#J 3/24/22 This function gets archiver data from start to end time for 
#           3 PVs per cavity for all 37
#           cryomodules and loads the data into three global dicts (resultsFB, 
#           resultsIntlk, resultsRfRdy) keyed to PV name
#
    global resultsFB, resultsIntlk, resultsRfRdy, startTime, endTime
    pvList=[]
    results={}
    cavPvRfRdy=[]
    cavPvFB=[]
    cavPvIntlk=[]
    cavPv=[]

    archiver=Archiver("lcls")

    #global cavPvFB, cavPvIntlk, cavPvRfRdy
    if (resultsFB == {}) or (strtTim != (time.mktime(datetime.datetime.strptime(strtTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))) or (endTime != int(time.mktime(datetime.datetime.strptime(endTim, '%m/%d/%Y %H:%M:%S' ).timetuple()))):
        print("We're in!")
        startTime = datetime.datetime.strptime(strtTim, '%m/%d/%Y %H:%M:%S' )
        endTime = datetime.datetime.strptime(endTim, '%m/%d/%Y %H:%M:%S' )
        print('Start time {}'.format(startTime))
        print('End time {}'.format(endTime))
        cavPv=makList()
# For after Sonya adds FB_SUM to the list
#        codeFlt = ["FB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
        codeFlt = ["PHAFB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
        for pv in cavPv:
            cavPvFB.append(str(pv)+codeFlt[0])
            cavPvIntlk.append(str(pv)+codeFlt[1])
            cavPvRfRdy.append(str(pv)+codeFlt[2])
        for pv in cavPv:
            for i in range(3):
                pvList.append(str(pv) + codeFlt[i])

        for pv in pvList:
            print('PV: {}'.format(pv))
            archiverData=archiver.getValuesOverTimeRange([pv],startTime,endTime)
            result={"times":[],"values":[]}
            result["values"]=archiverData.values[pv]
            for ts in archiverData.timeStamps[pv]:
# convert datetime to posix time
                result["times"].append(ts.timestamp()) 
            results[pv] = result

#        print(results)
        for cav in cavPvFB:
            resultsFB[cav]=results[cav]
        for cav1 in cavPvIntlk:
            resultsIntlk[cav1]=results[cav1]
        for cav2 in cavPvRfRdy:
            resultsRfRdy[cav2]=results[cav2]

    else:
       print('got elsed')
       return;



#******************************************************
##
#J 3/24/22 This is the function to load up the global arrays of results 
#          (see comments for GetValuesOverTimeRange) with dummy data
#
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
# for when sonya fixes it
#        codeFlt = ["FB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
        codeFlt = ["PHAFB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
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
#
    #   cmFlts determines the sum of the number of cryomodule faults from the global 
    #  resultsFB, resultsIntlk, resultsRfRdy Dicts  which are generated by the archiver calls
    #  ReWrite complete
##
#J 3/24/22 I loathe single character variable names-makes it so hard to search, so I doubled them.
#     Called by XfelDispTest2.py:
#        CmNumTop, CmNumLow, numFltsTop, numFltsLow, StDTop, StDLow = arPullGlob.cmFlts()
#     Function:
#          For each cavity in a given cryomodule the Intlk data is concatenated,
#          then summed/stdev into total and stDev variables.
#          These values are then divided into totalLo/stDLo for CM0-15 and
#          totalHi/stDHi for CM16-35.
#          A tuple of bb, cc, totalLo, totalHi, stDLo, stDHi is returned.
#          More elecgant to fill totalLo/Hi without intermediate total?
#          bb & cc seem to be lists of numbers 0..16 and 17..37, 
#          there's gotta be a better way to do that too.
#          aaaa is the list of interlock PVs (keys into results dict), one per cavity.
#          this allows the sum of the values for the 8 cav in each CM. Would search for 
#          CM string prefix be faster or more elegant than the numeric 0..7, 8..15, ? 
#
#    Bob's comment says he looks at all 3 global dicts rather but it's just resultsIntlk
##
    bb=[]
    cc=[]
    total=[]
    totalLo = []
    totalHi=[]
    stDev=[]
    stDLo=[]
    stDHi=[]

    aaaa=list(resultsIntlk.keys())
#    print('aaaa {}'.format(aaaa))
    for nn in range(0, 37):
        CMtot = []
        for ii in range(0, 8):
             tut=aaaa[ii+nn*8]
             CMtot.append(len(resultsIntlk[tut]['values']))

        total.append(numpy.sum(CMtot))
        stDev.append(numpy.std(CMtot))

    for ii in range(17):
            totalLo.append(total[ii])
            stDLo.append(stDev[ii])
            bb.append(ii + 1)
    for ii in range(17, 37):
            totalHi.append(total[ii])
            stDHi.append(stDev[ii])
            cc.append(ii - 1)

    return bb,cc,totalLo, totalHi, stDLo, stDHi;

#****************************************************

#****************************************************
##
#J 3/24/22 - doubled the index variables
#    Called from within cmStats:
#        dd=sortStats(CavFltDat,CavRdyDat)
#          returns FltTime
#     cavFltDat & CavRdyDat are the times when those PVs (INTLK_FIRST & RRFB) change state
#     He's looking for how long between recovery (RRFB->1) and previous trip 
#     As best as I can tell, he's returning a list of # of seconds of down for each trip
#     I think this algorithm could miss the first trip
#     Could we look at the RRFB values, watch for 0->1 and subtract previous 1->0 time?
#   at end he checks for if cavFaults=[] - needs to change to CavFlts presumably.
##
def sortStats(CavFlts, CavRdy):
    ii=0
    nn=0
    FltTime=[]
    dd=[]
    while ii <= (len(CavFlts) - 1):
       Flt = CavFlts[ii]
       Rdy = CavRdy[nn]

       if (int(Rdy) >= int(Flt)) and ((ii + 1) <= len(CavFlts)) and ((nn + 1) <= len(CavRdy)):
           FltTime.append(int(Rdy) - int(Flt))
           while (int(Flt) <= int(Rdy)) and ((ii + 1) <= len(CavFlts)):
              try:
                ii += 1
                if (ii + 1) <= len(CavFlts):
                   Flt = CavFlts[ii]
                continue
              except IndexError:
                #print("incremented ii too far")
                break

       elif (int(Flt) >= int(Rdy)) and ((nn + 1) < len(CavRdy)):
           try:
              while (Flt >= Rdy):
                nn += 1
                Rdy = CavRdy[nn]
                continue
           except IndexError:
              #print("incremented nn too far")
              break
       else:
           break
    if cavFaults==[]:
       FltTime=0

    return FltTime;
#***************************************************

#***************************************************
##
#J 3/24/22  doubled the single letter variables
#    Called in XfelDispTest2.cmStats: (don't confuse CmStats with cmStats...)
#       CmNumTop, CmNumLow, MeanRecTop, MeanRecLow, StDevRec, StDevRec2 = arPullGlob.CmStats()
#    Return statement:
#        return bb,cc,totalLo, totalHi, stDLo, stDHi;
#    bb/cc are lists of CM numbers 0-15 and 16-35
#    Top/Low refers to the two plots on the fault display gui
# TODO: What are the keys in the resultsIntlk dict? Is it just the INTLK_FIRST PVs?
#
def CmStats():
# Lisa says global isn't required - if PVs are at the top of the file, then they're global
    global resultsIntlk, resultsRfRdy
    bb=[]
    cc=[]
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

# get list of PV prefixes (ACCL:L0B:0110:, ...)
    pvList = makList()
# PV suffixes
#for when sonya fixes it
#    codeFlt = ["FB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
    codeFlt = ["PHAFB_SUM", "RFS:INTLK_FIRST", "RFREADYFORBEAM"]
#   for each cavity...
    for pv in pvList:
#       for all the interlock & RRFB PVs, get the times when PVs changed state
#        don't see why this needds to be str(pv)
        CavFltDat= (resultsIntlk[(str(pv)+ codeFlt[1])]['times'])
        CavRdyDat= (resultsRfRdy[(str(pv)+ codeFlt[2])]['times'])
#     get the recovery times for a single cavity - this is a list of # of seconds off for each trip
        dd=[]
        dd=sortStats(CavFltDat,CavRdyDat)
        #print dd
# This statement isn't needed
#        xx = numpy.array(dd)
#J 3/24/22 Change xx in cavTot statement to dd.
        # set division factor for appropriate unit of time; hours, min, or sec
# I don't understand why not 60/60/24 to get days? total is in seconds I think. Posix time is sec since 1/1/70
# cavTot is list of # of sec off for each CM
        cavTot.append(numpy.sum(dd)/60.0/60/60)
###
# What about
#    downtimeArr=np.reshape(cavTot,(37,8))
#    totalLo=np.sum(downtimeArr,1).tolist()[0:17]
#    stDLo=np.std(downtimeArr,1).tolist()[0:17]
#    totalHi=np.sum(downtimeArr,1).tolist()[17:]
#    stDHi=np.std(downtimeArr,1).tolist()[17:]
#    bb=list(range(17))
#    cc=list(range(17,37))
###

    #print(len(cavTot))
# for each CM...
    for nn in range(0,37):
        CMtot=[]
        for ii in range(0,8):
            indCav = ii + nn*8.0
# make a list of its 8 cavities' downtimes
            CMtot.append(cavTot[int(indCav)])
# Then sum, average, and get stdev for those 8 numbers
        total.append(numpy.sum(CMtot))
        average.append(numpy.mean(CMtot))
        stDev.append(numpy.std(CMtot))
#    print(total)
    for ii in range(17):
        totalLo.append(average[ii])
        stDLo.append(stDev[ii])
        bb.append(ii+1)
    for ii in range(17,37):
        totalHi.append(average[ii])
        stDHi.append(stDev[ii])
        cc.append(ii-1)
    return bb,cc,totalLo, totalHi, stDLo, stDHi;
#***************************************************

#***************************************************
def makCavPv(spinOut):
##
#J 3/24/22 fix the single letter variables...
#   Called by cavFaults and cavStats:
#    pvCav, cavU = makCavPv(cmUpper)
#    pvCav, cavL = makCavPv(cmLower)
#
#   takes the output of the combo box (00, 01, 02, H1, H2, 03, ... 35)
#    and returns pv2=ACCL:LxB:CM(10, 20, ..., 80) for just one CM 
#    and cav=CM-(10, 20, ..., 80)
#   presumably for axis labels?
##
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
    for ii in range(1, 9):
        alpha = pvL + str(ii) + "0"
        # print(alpha)
        pv2.append(alpha)
# use str(dig).zfill(2) to get 01, 02, ... 10, ...37
# What type is spinOut? works for both strings and ints!
        if len(str(spinOut)) == 1:
            cav.append("0"+str(spinOut) + "-" + str(ii) + "0")
        else:
            cav.append(str(spinOut)+"-"+str(i)+"0")
    if str(spinOut) == "Not":
        pv2 = "NaN"
    return pv2, cav;
#***********************************************
##
#J 3/24/22
#    Called by cavFaults
#    resP = cavDatCnt(pvCav,Start, End) for upper and resP2= for lower
#     pvCav is output of makCavPv, start and end are passed into cavFaults
#     pvCav=['ACCL:LxB:CM10', 'ACCL:LxB:CM20', ..., 'ACCL:LxB:CM80']
#     sT and fiN are unused. 
#     bozo is the dictionary with the different types of faults (PLL lock, ioc watchdog etc) 
#        as the keys and the values are the number of times those fault occurred.
#     clown is the INTLK_FIRST archiver values which are then counted to fill out bozo
#    returns: dictionary results[pvl]=bozo, pvl is one CM's <prefix>:RFS:INTLK_FIRST
#     originally (deleted the comments) the code got the data from the archiver thus it needed st & fin
##
def cavDatCnt(caVs, sT, fiN):
    results={}
    if caVs != "NaN":
        for pv in caVs:
            #
            #  bozo and clwn are variables to count the number for each type of fault in the dataset
            #  fault code '1' is PLL lock, '2' is ioc watchdog, '4' is the Interlock Fault summary, '8' is Comm fault
            #  '16' is an SSA fault and '32 is a cavity quench
            #
            pvL=pv+':RFS:INTLK_FIRST'
# for when Sonya fixes it
#            pvFB = pv+":FB_SUM"
            pvFB = pv+":PHAFB_SUM"
#            print('pvFB {}'.format(pvFB))
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
            bozo["Clips"] = len(resultsFB[pvFB]['values']) # was ["values"]
            results[pvL] = bozo
    else:
        results = []
    return results;
#
#***********************************************
##
#J 3/24/22
#   Called by XfelDispTest2.cavFaults (not kidding)
#    CavNumTop, CavNumLower, CavFaultsUpper, CavFaultsLower = arPullGlob.cavFaults(OutTextUpper, OutTextLower, StTim, EnTim)
#      OutTextUpper -> cmUpper = upper CM spinner, OutTextLower -> cmLower = lower CM spinner
#        makCavPv returns  ['ACCL:LxB:CM10',...,'ACCL:LxB:CM80'],['CM-10','CM-20',...]
#        cavDatCnt returns dictionary keyed by PV prefix +RFS:INTLK_FIRST with dictionary as value which
#          has fault types as keys and # of that type of fault as values
#   Returns  cavU, cavL, resP, resP2;
#     cavU is CM-## for upper, cavL is CM-## for lower, 
#      resP is fault type dictionary for upper CM, resP2 is lower.
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
##
#J 3/24/22 doubled the single letter variable names, which aren't used...
#  called by cavStats twice - once for each spinner:
#          resPave, resPstd = cavStatCnt(pvCav,Start,End)
#         pvCav is the 8 prefixes for a given CM
#         start and end are no longer used (deleted commented code that called archiver)
# For each of the 8 cavities, he gets a list of seconds down for each trip then 
#    gets the mean and std of that list, divides by 60 to get minutes and appends
#     to lists cavAve and cavStD which are returned:
#       return cavAve, cavStD;
def cavStatCnt(Cav, Start, End):
     cc="00"
     dd=[]
     xx=[]
     cavAve=[]
     cavStD=[]
     results={}
     results2 ={}

     for ca in Cav:
        caP = ca +":RFS:INTLK_FIRST"
        caR = ca + ":RFREADYFORBEAM"

        results[ca]=sorted(resultsIntlk[caP]["times"])  #this is the time of the faults
        results2[ca]=sorted(resultsRfRdy[caR]["times"])  # this is the time that rf shows fully recovered
#        print(ca,results[ca],results2[ca])
#J aaaa is pvprefix+"RFS:INTLK_FIRST"
     aaaa = results.keys()
#     print(aaaa)
     for cav in aaaa:
        ii = 0
        nn = 0
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
##
#J 3/24/22
#  Called by cavStats in XfelDispTest2 (still not kidding):
#    CavNumTop,CavNumLower,cavRec,cavRecStDev, cavRec2,cavRecStDev2 = arPullGlob.cavStats(OutTextUpper, OutTextLower, StTim, EnTim)
#      OutTextUpper -> cmUpper = upper CM spinner, OutTextLower -> cmLower = lower CM spinner
#     pvCav is pv prefixes for one CM, cavU/L is ['CM-10','CM-20',...]
#     resPave, resPstd are the ave/std amounts of time in minutes that a cavity is off
#  Returns:
#     return cavU, cavU2, resPave, resPstd, resPave2, resPstd2;
#
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
##
#J 3/24/22 fix the single letter variables
#     Called by xFelDisplay in XfelDispTest2 (still not kidding...)
#        squid = arPullGlob.XfelDsply(StTim)
#   aaaa is all the PVs that end in RFS:FIRST_INTLK (all 37*8 of them)
#   for each cavity, get the times that it tripped (FIRST_INTLK has value in archiver)
#      for each of the trips, figure out the date of the trip and calculate how 
#       many days between the trip and 7/22/2021 then append that number to CMtot
#       Then find the unique numbers of dates (days since 7/22/21) and 
#       how many trips on each of those dates and return that as a tuple
#        fltCount[nn] = fltDay["day"],fltDay["value"]
# returns fltCount

# I think he's assume that sort culls duplicates, 
#    np.unique sorts and culls but returns an ndarray so
#    mylist=np.unique(cmtot).tolist() then count in cmtot
#
def XfelDsply(strt):
    bb=[]
    vTime=[]
    totalLo=[]
    totalHi=[]
    fltCount = {}

   # begin = datetime.date(strt.strftime('%Y,%m,%d'))
    begin= datetime.date(int(2021),int(7),int(22))

    aaaa=list(resultsIntlk.keys())
    for nn in range(0, 37):
        CMtot = []
        mylist = []
        fltDay = {"day": [], "value": []}
        for ii in range(0, 8):
             tut=aaaa[ii+nn*8]
#             print(tut)
             vTime= sorted( resultsIntlk[tut]['times'])
             for vv in vTime:
                 bb=(datetime.date.fromtimestamp(vv))
#                 print(n,i,b)
                 daysCnt = bb - begin
#                 CMtot.append(datetime.datetime.strftime(b, '%d'))
                 CMtot.append(int(daysCnt.days))

                 mylist = list(dict.fromkeys(CMtot))
        mylist.sort()
        for CMc in mylist:
             fltDay["day"].append(int(CMc))
             fltDay["value"].append(CMtot.count(str(CMc)))
        fltCount[nn] = fltDay["day"],fltDay["value"]
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
    

