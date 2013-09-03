#!/usr/bin/python

import Telldus.Controller
import MacroParser.Macros


"""This is a simple script called if one would like to start a wakeup sequene
without having the whole server running. """

tc = Telldus.Controller.TelldusController()
    
tc.start()
    
    
#wum = MacroParser.Macros.wakeup_macro(1)
macro = None




try:
    #macro = MacroParser.Macros.wakeup_macro(1)
    macro = MacroParser.Macros.xml_macro("/home/fredrik/workspace/TelldusController/src/xml/morningscenario.xml")
except Exception as e:
    print "error: %s" % e
else:
    macro.start()
        
    macro.join()
        
    # Tell the Telldus Controller to stop running.
tc.should_be_running = False
