from datetime import datetime
from lcls_tools.data_analysis.archiver import Archiver, ArchiverData
import matplotlib.pyplot
import matplotlib.dates


archiver=Archiver("lcls")

strtTime='3/22/2022 19:03:00'
startTime=datetime.strptime(strtTime,'%m/%d/%Y %H:%M:%S')
endTime=datetime.now()

archiverData=archiver.getValuesOverTimeRange(['BEND:LTUH:220:BACT'],startTime,endTime)

datavals=archiverData.values['BEND:LTUH:220:BACT']
datatims=archiverData.timeStamps['BEND:LTUH:220:BACT']

dates=matplotlib.dates.date2num(datatims)
matplotlib.pyplot.plot_date(dates,datavals)
matplotlib.pyplot.show()
