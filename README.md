# Fault-Display
This is the latest Fault display code for LCLSII.  It is based on an archiver pull to look for faults over time with limited statistics built-in.
The fault logger is actually a display program which pulls rf flt data  from the archiver and manipulates it for display.  
Because there presently is no archiver for LCLS-II, the program uses randomly generated data for testing.  The archiver pull
portion was tested using a set of bend magnet PVs from the copper linac.  
The four files which are required to run the program under pydm are: the two user interface displays, FltDisp.ui and CMSelector.ui, and 
the two python files, XFelDisplayTest2.py and arPull.py.  The XFelDisplayTest2.py file manages the 'GUI' and user inputs.  It generates
messages for the display based on user actions and pulls the .ui inputs and processes them into requests for data. It passes the requests 
for arrays of fault data over a specified time to the arPull.py program which does the archiver pulls and separates the data into types of
faults and generates recovery statistics.  The arPull.py program can be run standalone in a python (not pydm) enviroment to test archiver
interface, numeric manipulation and arrays for display generation.  Common test functions are contained in the __init__main at the bottom.

The **back version of the file pops up the XFEL fault plot in a separate display.  This might be preferable if using the plot for a presentation.  The XFEL type display shows the days from now at the bottom, so if no date is selected,  you'll see about -7000 days (since 2000).  
