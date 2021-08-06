from pydm import Display
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import (QWidgetItem, QCheckBox, QPushButton, QLineEdit,
                             QGroupBox, QHBoxLayout, QMessageBox, QWidget,
                             QLabel, QFrame, QComboBox, QRadioButton)
from os import path, pardir
from qtpy.QtCore import Slot
# from pydm.widgets.template_repeater import PyDMTemplateRepeater
#from typing import List, Dict
from functools import partial, reduce
from datetime import datetime, timedelta
import sys
import numpy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from random import randint, random
import datetime
import arPullGlob



i=0

class MplCanvas(FigureCanvasQTAgg):
# MPLCanvas is the class for the 'canvas' that plots are drawn on and then mapped to the ui
# They are Figure format described in matplotlib 2.2 documentation

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout="true")
        self.axes = fig.add_subplot(111)
        #fig.align_labels()  This was removed since only available in version 3 and later of matplotlib

        super(MplCanvas, self).__init__(fig)


class FltDisp(Display):

    def __init__(self, parent=None, args=None, ui_filename="FltDisp3.ui"):
        super(FltDisp, self).__init__(parent=parent, args=args, ui_filename=ui_filename)
        self.pathHere = path.dirname(sys.modules[self.__module__].__file__)

        self.ui.RfFltSel.addItems(["RF Faults over time", "Fault Stats over Time", "Faults per module by Day"])
        self.ui.RfFltSel.currentIndexChanged.connect(self.show_result)

        def getPath(fileName):
            return path.join(self.pathHere, fileName)  # This is supposed to find the path to the file named
                                                       # so that the files don't always have to be in the same dir
        UpperPlot = MplCanvas(self, width=5, height=4, dpi=100)  #This defines the plot sizes and attributes
        LowerPlot = MplCanvas(self, width=5, height=4, dpi=100)  # as matplotlib Figures
        XfelPlot = MplCanvas(self, width = 5, height =10, dpi=100)
        
        self.ui.Plot1.addWidget(UpperPlot)                       # write the UpperPlot Figure as a widget to the Plot1
                                                                 # frame in the FltDisp.ui pydm display
        self.ui.Plot2.addWidget(LowerPlot) 
        #self.ui.Plot2.addwidget(XfelPlot)                     # Write the LowerPlot Figure as a widget to the
                                                                 # Plot2 frame in the FltDisp.ui
        #self.ui.frame_5.addWidget(XfelPlot)
        
        self.selectWindow = Display(ui_filename=getPath("CMSelector.ui"))  # Set the 'selectWindow' to the cryomodule
#        self.xfDisp =Display(ui_filename=getPath("XfelDisp.ui"))   
#        self.xfDisp.ui.Plot3.addWidget(XfelPlot)
        self.ui.CMSelection.clicked.connect(self.CM_Sel)                   # When the CMSelection button is clicked,
                                                                           # call the function to display the ui
        # The idea was to have the user input happen on the displays, but only use the values and build plots
        #  when the 'GO' button was pushed.  Since once the GO is pushed, the code has to write new plots to the Plot1
        #  and Plot2 frames,  the UpperPlot and LowerPlot names are passed to the setGOVal function.
        self.ui.GO.clicked.connect(partial(self.setGOVal,UpperPlot,LowerPlot))

    def show_result(self,i):
        spinVal = i
        dispVal = self.ui.RfFltSel.currentText()
#        print(spinVal, dispVal)
        
    def CM_Sel(self):                                  # This pops up the CMSelector.ui and writes text to the
        self.showDisplay(self.selectWindow)            # "Sel_Instructions label" in the ui
        self.selectWindow.ui.Sel_Instructions.setText("One Cryomodule may be selected for each of the Upper and Lower plots")


    def setGOVal(self,ac, ac2):
        cmNumUpper = self.selectWindow.ui.Plot_1.value()  # Get Cryomodule number from spinner in CMSelector.ui
                                                          # for individual display in upper plot in FltDisp.ui
        cmNumLower = self.selectWindow.ui.Plot_2.value()  # Get Cryomodule number from spinner in CMSelector.ui
                                                          # for individual display in lower plot in FltDisp.ui
        HUpper = self.selectWindow.ui.HS_Upper.value()    # Get 'H' cryomodule (3rd Harmonic) from spinner
                                                          # in CMSelector.ui  for upper plot in FltDisp.ui
        HLower = self.selectWindow.ui.HS_Lower.value()    # Get 'H' cryomodule (3rd Harmonic) from spinner
                                                          # in CMSelector.ui  for lower plot in FltDisp.ui
        val = self.ui.StartTime.dateTime()                # Get the start time for the Archiver pull
        val2 = self.ui.EndTime.dateTime()                 # Get the ending time for the Archiver pull
                                                          # 'val' variables are used to be compatible with toPyDateTime
                                                        # function below to get times in format which Archiver requires
        StTimeForArchiver = val.toPyDateTime().strftime('%m/%d/%Y %H:%M:%S')  #  All about the format
        EndTimeForArchiver = val2.toPyDateTime().strftime('%m/%d/%Y %H:%M:%S')
        #print(StTimeForArchiver)
        if EndTimeForArchiver > StTimeForArchiver:   # Checks that the End time is after the Start time
            #arPullGlob.getValuesOverTimeRange(StTimeForArchiver, EndTimeForArchiver)
            #  Use Dummy value generator for now
            arPullGlob.getValuesOverTimeDummy(StTimeForArchiver, EndTimeForArchiver)
            if (cmNumUpper!= 0 and HUpper != 0) or (cmNumLower != 0 and HLower != 0):  # This checks if more than one
                                                      # cryomodule is selected to be plotted, if two are selected
                                                      # an error message is written and breaks out of GO function
                self.selectWindow.ui.Sel_Instructions.setText("Only one CM per plot.  Try again")

            elif ((cmNumUpper == 0 and HUpper == 0) and (cmNumLower == 0 and HLower == 0)):  # check if no CMs selected
                self.selectWindow.close()             # if so, close CMSelector.ui
                self.ui.Changes.setStyleSheet("color: red;")              #  change the text color to red
                self.ui.Changes.setText("No Cryomodules Selected.")       # and write to label 'Changes' in FltDisp.ui

                if int(self.ui.RfFltSel.currentIndex()) == 0 :                        #If no CM selected and if RfFaults radiobutton
                                                                        # is checked, call the function, cmFaults,
                     # which asks the arPull module for arrays of first fault and clip data for all modules
                     #
                     self.cmFaults(ac,ac2)
                elif int(self.ui.RfFltSel.currentIndex()) == 1 :
                        # Otherwise call the function, 'cmStats' which
                                              # calls the arPull module to get faults and recovery times for all modules
                     self.cmStats(ac,ac2)
                else: 
                     self.xFelDisplay(ac,ac2,val,val2)
            else:                             # Else, there is a non-zero value on the CM selector spinners
                self.selectWindow.close()     # Close the selector display
                self.ui.Changes.setStyleSheet("color: green;")   # write in green
                if cmNumUpper != 0:                   # Need to check that upper CM selector != 0 before reading value
                     OutTextUpper = cmNumUpper        # if so,grab the value
                elif HUpper != 0:                     # Is the 3rd Harmonic spinner non-zero?
                     OutTextUpper = "H" + str(HUpper) # if so, grab         print(pvCav)that value
                else:                                 # If neither cryomodule nor 3rd harmonic is selected
                     OutTextUpper = "Not"             # set value to "Not" so arPull won't grab data

                if cmNumLower != 0:                    # Need to check that lower plot CM selector != 0 before
                     OutTextLower = cmNumLower         # reading value. if so,grab the value
                elif HLower != 0:                      # Is the 3rd Harmonic spinner non-zero?
                     OutTextLower = "H" + str(HLower)  # if so, grab that value
                else:                                  # If neither cryomodule nor 3rd harmonic is selected
                     OutTextLower = "Not"              # set value to "Not" so arPull won't grab data

                StrOut = ("CM " + str(OutTextUpper) + " selected. CM " + str(OutTextLower) + " selected.")
                self.ui.Changes.setText(StrOut)       # write the numbers of the CMs selected to the ui label "Changes"
                # if it gets to here, a cm was selected.
                if int(self.ui.RfFltSel.currentIndex()) == 0 :        #If the RfFaults radiobutton is selected, call cavFaults function
                     self.cavFaults(ac, ac2, OutTextUpper,OutTextLower,StTimeForArchiver, EndTimeForArchiver)
                elif int(self.ui.RfFltSel.currentIndex()) == 1 :                                #If the RF Stats radiobutton was selected, call cavStats function
                     self.cavStats(ac, ac2, OutTextUpper,OutTextLower,StTimeForArchiver, EndTimeForArchiver)
                else: 
#                     self.xFelDisplay(ac3,StTimeForArchiver,EndTimeForArchiver)
                     self.xFelDisplay(ac,ac2,val,val2)
        else:                            # if start time is after end time, write to display to try again
            self.ui.label_3.setText("Start before End. Try again")


#  All the display functions, cmFaults, cmStats, cavFaults and cavStats below are only display functions.
#  The call the archiver pull functions from the arPull module. The pull functions also manipulate the data
#  to generate the list arrays which matplotlib can plot and pass those back to the display functions
#  for plotting.  The arPull functions are standalone in python and at the bottom of the code in the init__main
#  there are test cases which can be uncommented for test purposes.
    # called from the setGOVal function after it branches to determine correct plot function to call
#
    def cmFaults(self,ac,ac2):             # This is function to plot cryomodule faults
                                                       # ac and ac2 are the names of the canvases the matplotlib plots
                                                       # are drawn in. ac is the upper frame. ac2 is the lower frame.
# CmNumTop and CmNumLow are the arrays for the CMs labels for the upper and lower plots.  Nom is 1-15 top (15@1.3's and
                                                       #  2@3.9's) and 16 through 35 on the lower plot (L3B).
# numFltsTop and numFltsLow are the arrays for the numbers of faults in the CM's in the upper and lower plots.
# Nom is 1-15 top (15@1.3's and 2@3.9's) and 16 through 35 on the lower plot (L3B).
# StDTop, StDLow are the arrays for the Standard Deviation between the number of cavity faults with in the CM.
                                                       #
        CmNumTop, CmNumLow, numFltsTop, numFltsLow, StDTop, StDLow = arPullGlob.cmFlts()

# call the function in arPull module with Start Time for Data (StTim) and the End Time for Data
# times need to be in format archiver will accept.
        self.ui.label_3.setText("Faults vs Cryomodule")
        self.ui.label_7.setText("Blue Bars are RF Faults. Black lines are StDev of Cavity Faults")
        ac.axes.cla()                            # bar chart of number of Faults vs CM with StDev as the error bars
        ac.axes.bar(CmNumTop, numFltsTop, yerr=StDTop)
        ac.axes.set_xlim(0,18)                   # this version of matplotlib is dumb.  Explicit set of axis limits
        ac.axes.set_ylabel('Faults')
        ac.axes.set_xlabel('L0B   L1B  HS                  L2B                       ')
        ac2.axes.cla()                            # bar chart of number of Faults vs CM with StDev as the error bars
        ac2.axes.bar(CmNumLow, numFltsLow, yerr=StDLow )
        ac2.axes.set_xlim(15,36)                  # this version of matplotlib is dumb.  Explicit set of axis limits
        ac2.axes.set_ylabel('Faults')
        ac2.axes.set_xlabel('L3B')
        ac.draw_idle()                      # This is the magic command that redraws the plot in the upper ui frame
        ac2.draw_idle()                     # This is the magic command that redraws the plot in the lower ui frame



    def cmStats(self,ac,ac2):
        # called from the setGOVal function after it branches to determine correct plot function to call
        # ac and ac2 are names for the canvases that matplotlib will draw on for plotting.
        # ac is the upper canvas, ac2 is the lower canvas (see ui if confused)
# Call to function CmStats in arPull module giving Start and end time.  It queries the archiver and returns arrays
                                                       # for display by ui
        CmNumTop, CmNumLow, MeanRecTop, MeanRecLow, StDevRec, StDevRec2 = arPullGlob.CmStats()
        #CmNumTop = [1,2,3,4,5,6,7,8,9,10]
        #CmNumLow = [16,17,18,19,20,21,22,23,24,25]
        #MeanRecTop = [3,2,1,3,4,5,3,2,3,7]
        #MeanRecLow = [6,2,3,2,4,1,3,4,2,3]
        #StDevRec = [1.1, 1.5,1.4,1.4,1.3,1.5,1.6,1.4,1.5,2.3]
        #StDevRec2 = [1.4, 1.5,1.2,1.2,1.2,1.3,2,1.3,1.5,1.3]
# CmNumTop and CmNumLow are the arrays for the CMs labels for the upper and lower plots.  Nom is 1-15 top (15@1.3's and
                                                       #  2@3.9's) and 16 through 35 on the lower plot (L3B).
# MeanRecTop and MeanRecLow are the arrays of the average recovery time for cavities in a CM for the
        # upper plot (L0B, L1B and L2B) and the lower plot (L3B).  StDevRec and StDevRec2 are the arrays of
        # the Std Dev between the mean recovery times for the cavities in each cryomodule.
                        #  Couple of writes to ui to tell user what is being displayed
        self.ui.label_3.setText("Rec Stats vs Cryomodule")
        self.ui.label_7.setText("Blue Bars are Mean Rec time for CM faults. Black lines are StDev")
        ac.axes.cla()                       # bar chart of average recovery time vs CM with StDev as the error bars
        ac.axes.bar(CmNumTop, MeanRecTop, yerr=StDevRec)
        ac.axes.set_xlim(0,18)              # this version of matplotlib is dumb.  Explicit set of axis limits
        ac.axes.set_ylabel('Ave Rec T, min')
        ac.axes.set_xlabel('L0B   L1B  HS                 L2B                       ')
        ac2.axes.cla()                     # bar chart of average recovery time vs CM with StDev as the error bars
        ac2.axes.bar(CmNumLow, MeanRecLow, yerr=StDevRec2)
        ac2.axes.set_xlim(15,36)           # this version of matplotlib is dumb.  Explicit set of axis limits
        ac2.axes.set_ylabel('Ave Rec T, min')
        ac2.axes.set_xlabel('L3B')
        ac.draw_idle()                     # This is the magic command that redraws the plot in the upper ui frame
        ac2.draw_idle()                    # This is the magic command that redraws the plot in the lower ui frame
#


    def plotOne(self,frAme,cav,reS, OutText):
# plotOne is function which takes the frame name to plot to, the cavity name "cav" (01-10 format) listthat goes with the data
# array for the plot labels, and "reS" a dict with an entry for the number of each type of fault for each cavity
# data structure looks like:
# {'ACCL:L2B:410': {'PLLlock': 0, 'iocDog': 0, 'IntlkFlt': 0, 'CommFlt': 0, 'SSAFlt': 0, 'Quench': 0, 'Clips': 1}
#  "OutText" is the output text from the selector ui which tells which CM was selected for plotting
#  Called from cavFaults function

# this is just initializing the arrays for faults so matplotlib can plot them
        PLL = []
        qnch = []
        ioc = []
        SSA = []
        Intlk = []
        com = []
        twill = []
        plaid = []
        suede = []
        silk = []
        gingham = []
        clip = []

#****************
# frAme is the canvas (frame) in the .ui being plotted to
# reS is the array (dict) of the faults by cavity passed back from the arPull.py module, see above
# The fabric variables are needed since matplotlib wants an offset from the baseline to write multiple bars
# on top of one another using the 'bottom' parameter.  The fabrics are the fault number by cavity and type added
# together in arrays.

        pVu = reS.keys() 
#        print(pVu)                                   # make a list of the cavity names in the dict
        for testPV in pVu:                                  # iterate on those names
            PLL.append(reS[testPV]["PLLlock"])   #append the # of PLLLock faults for the testPV cavity to the list 'PLL'
            qnch.append(reS[testPV]["Quench"])   # and repeat for quench faults to the 'qnch' list
            twill.append(reS[testPV]["Quench"] + reS[testPV]["PLLlock"])  # frAme.axes.bar wants a list for the 'bottom' parameter
            ioc.append(reS[testPV]["iocDog"])
            plaid.append(reS[testPV]["Quench"] + reS[testPV]["PLLlock"] + reS[testPV]["IntlkFlt"])  # the fabric variables make the bars stack nice
            SSA.append(reS[testPV]["SSAFlt"])
            suede.append(reS[testPV]["Quench"] + reS[testPV]["PLLlock"] + reS[testPV]["IntlkFlt"] + reS[testPV]["iocDog"])
            Intlk.append(reS[testPV]["IntlkFlt"])
            gingham.append(
                reS[testPV]["Quench"] + reS[testPV]["PLLlock"] + reS[testPV]["IntlkFlt"] + reS[testPV]["iocDog"] + reS[testPV][
                    "SSAFlt"])
            com.append(reS[testPV]["CommFlt"])   # and repeat for 'com' faults
            silk.append(
                reS[testPV]["Quench"] + reS[testPV]["PLLlock"] + reS[testPV]["IntlkFlt"] + reS[testPV]["iocDog"] + reS[testPV][
                    "SSAFlt"] + reS[testPV]["CommFlt"])        # stack up all the array below it
            clip.append(reS[testPV]["Clips"])    # and finally get the 'clip' faults.
   
        ticks = numpy.arange(len(cav))  #  Get tick marks for the x axis since old matplotlib has to use numeric index
        frAme.axes.bar(ticks, qnch, align='center', label='Quench',color='b')  # align to center or plot bars are skewed
        frAme.axes.bar(ticks, PLL, bottom=qnch, align='center',label='PLL', color='g')   # Dumb matplotlib no auto palet
        frAme.axes.bar(ticks, ioc, bottom=plaid, align='center',label='IOC Watchdog',color='SkyBlue')
        frAme.axes.bar(ticks, SSA, bottom=suede, align='center',label='SSA Flt', color='IndianRed')
        frAme.axes.bar(ticks, Intlk, bottom=twill,align='center', label='Intlk Flt Sum',color='m')
        frAme.axes.bar(ticks, com, bottom=gingham,align='center', label='Comm Fault',color='c')
        frAme.axes.bar(ticks, clip, bottom=silk,align='center', label='Clip',color='r')
        frAme.axes.set_xticks(ticks)                                           # put tick marks across the x axis
        frAme.axes.set_xticklabels(cav)                                  # use the 'cav' array as the labels
        frAme.axes.legend(fontsize='xx-small',framealpha=0.3)
        frAme.axes.set_xlabel('Cavities in CM '+str(OutText))
        frAme.axes.set_ylabel('# of faults')
        frAme.axes.grid()                      
        frAme.draw_idle()                      # This is the magic command that redraws the plot in the lower ui frame

#
    # same rif as previously.  ac and ac2 are the names of the canvases that plots are created on and then they are
    # drawn on the frames in the ui.  OutTextUpper and OutTextLower are the text values for the cryomodules
    # selected for the upper and lower plots.  StTim and EnTim are the start and End times.
    # cavFaults is called to plot the cavity faults for the cryomodules described in the text during the time specified.
    # To do that they call arPull function to get data arrays.
    # called from the setGOVal function after it branches to determine correct plot function to call
    #
    def cavFaults(self,ac,ac2,OutTextUpper,OutTextLower,StTim,EnTim):
    # CavNumTop is list of cavities for upper plot. CavNumLower is list of cavities for lower plot.
    # CavFaults Upper and Lower are arrays of faults (see plotOne comments above) to be parsed and displayed
        
        CavNumTop, CavNumLower, CavFaultsUpper, CavFaultsLower = arPullGlob.cavFaults(OutTextUpper, OutTextLower, StTim, EnTim)
        self.ui.label_3.setText("Faults vs Cavity")
        self.ui.label_7.setText("Number of each flt type by Cavity for given time")
        ac.axes.cla()                                                # clear the upper canvas
        if OutTextUpper != "Not":                                    # If there is a cryomodule to be plotted,
            self.plotOne(ac,CavNumTop,CavFaultsUpper,OutTextUpper)   # Call plotOne and pass the data to plot it
        else:
            e = []                                                   # If no cryomodule specified by user
            cavRec = []                                              # draw an empty plot
            ac.axes.bar(CavNumTop, cavRec)
            ac.draw_idle()
        ac2.axes.cla()                                               # clear the lower canvas
        if OutTextLower != "Not":                                    # if there is a module to plot
            self.plotOne(ac2,CavNumLower,CavFaultsLower,OutTextLower)   # call plotOne function to plot datums
        else:                                                        # if no module is specified,
            e = []
            cavRec = []
            ac2.axes.bar(CavNumLower, cavRec)                        # make an empty plot
            ac2.draw_idle()                                          # amd draw it to the ui


    def cavStats(self,ac,ac2,OutTextUpper,OutTextLower,StTim,EnTim):
        # cavStats is called to plot the cavity recovery time stats for a cryomodule specified in 'OutTextxxxx' for the
        # upper and lower plots analogous to cavFaults function.
        # ac and ac2 are the canvas names again.
        # called from the setGOVal function after it branches to determine correct plot function to call
        #
       
        CavNumTop,CavNumLower,cavRec,cavRecStDev, cavRec2,cavRecStDev2 = arPullGlob.cavStats(OutTextUpper, OutTextLower, StTim, EnTim)
        # cavRec and cavRecStDev are the mean cavity recovery time and the standard deviation between the events for top plot
        # cavRec2 and cavRecStDev2 are the mean cavity recovery time and the standard deviation between the events for lower plot
        #the function arPull.cavStats calls the archiver and then sorts and substracts the data to get recovery times
        # inputs are the same, upper and lower module names in text and Start and End times in a for the archiver will accept
        #
        self.ui.label_3.setText("Rec Stats vs Cavity")                          # this just changes the labels above the plot
        self.ui.label_7.setText("Bars are mean Cav flt rec times. Lines are StDev") # to help the user know what is displayed
        ac.axes.cla()                                          # clear the upper plot
        ticks = numpy.arange(len(CavNumTop))       # OLD version of matplotlib requires numeric array to plot use length
        if OutTextUpper == "Not":                              # if no cyromodule selected,
            CavNumTop=[]                                       # set to empty arrays
            cavRec=[]
            cavRecStDev = []
        error_config = {'ecolor': '0.3'}           # more work arounds to work with OLD matplotlib
        ac.axes.bar(ticks, cavRec, yerr=cavRecStDev, error_kw=error_config, align='center',label='Rec time')
        #This actuals specifies the plot with ticks vs recovery time lists.  Standard Devs are in yerr (the error bars)
        ac.axes.set_xticks(ticks)                 # work around to put ticks on axis
        ac.axes.set_xticklabels(CavNumTop)        # put labels on ticks on axes
        ac.axes.set_ylabel('Rec time, min')
        ac.axes.set_xlabel('Cavities in CM '+str(OutTextUpper))      # put the CM displayed on label
        ac.draw_idle()                            # and draw the plot to the frame in the ui

        if OutTextLower == "Not":                 # if no cryomodule selected for lower plot,
            CavNumLower=[]                        # use empty lists to blank the plot
            cavRec2=[]
            cavRecStDev2 = []
        ticks2 = numpy.arange(len(CavNumLower))   # matplotlib 2.2 only plots numeric lists.  This is a workaround
        ac2.axes.cla()                            # clear the lower plot
        ac2.axes.bar(ticks2, cavRec2, yerr=cavRecStDev2, error_kw=error_config, align='center',label='Rec time')
        # This actuals specifies the plot with ticks vs recovery time lists.  Standard Devs are in yerr (the error bars)
        ac2.axes.set_xticks(ticks2)               # work around to put ticks on axis
        ac2.axes.set_xticklabels(CavNumLower)               # put labels on ticks on axes
        ac2.axes.set_ylabel('Rec time, min')
        ac2.axes.set_xlabel('Cavities in CM '+str(OutTextLower))
        ac2.draw_idle()                           # And draw the plot to the frame in the ui

    def xFelDisplay(self, ac,ac2, StTim,EnTim):
        #self.showDisplay(self.xfDisp)
        squid = []
        zzz = []
        days = []
        cmNumb=[]
        totalHi=[]
        totalLo=[]
        durTest=StTim.daysTo(EnTim)
        labStart= StTim.toString('d MM yy')
        labEnd = EnTim.toString('d MM yy')
#        print(labStart, labEnd)
        squid=arPullGlob.XfelDsply(StTim) 
        for i in range(17):
           days.append(squid[i][0])
           zzz.append(squid[i][1])
           for n in range(len(squid[i][0])):
              cmNumb.append(int(i))
        daysA=numpy.concatenate([numpy.array(i) for i in days])
        zzzA = numpy.concatenate([numpy.array(i) for i in zzz])
 
        ac.axes.cla()  
        ac.axes.scatter(daysA, cmNumb, c=zzzA)
        ac.axes.set_title('Color of dot indicates number of Faults')
        ac.axes.set_xlabel('Days from '+str(labStart)+' to '+str(labEnd))
        ac.axes.set_ylabel('Modules')
        ac.axes.grid(True)
        ac.draw_idle()
        
        days=[]
        zzz=[]
        daysA=[]
        zzzA=[]
        cmNumb=[]
        for i in range(17,37):
             days.append(squid[i][0])
             zzz.append(squid[i][1])
             for n in range(len(squid[i][0])):
                 cmNumb.append(int(i))
        daysA=numpy.concatenate([numpy.array(i) for i in days])
        zzzA = numpy.concatenate([numpy.array(i) for i in zzz]) 
        ac2.axes.cla()  
        ac2.axes.scatter(daysA, cmNumb, c=zzzA)
        ac2.axes.set_title('Color of dot indicates number of Faults')
        ac2.axes.set_xlabel('Days from '+str(labStart)+' to '+str(labEnd))
        ac2.axes.set_ylabel('Modules')
        ac2.axes.grid(True)
        ac2.draw_idle()
            
    
    def showDisplay(self, display):
        # type: (QWidget) -> None
        display.show()
        # brings the display to the front
        display.raise_()
        # gives the display focus
        display.activateWindow()
