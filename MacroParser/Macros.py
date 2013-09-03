#!/usr/bin/python

import threading
import time
import glob
import MacroParser
import Telldus



class MacroCollection(object):
    """This is a collection of macros defined in xml format that are read from
    a list of folders.
    
    Attribute:
        folder_list -- The list with the paths from where to collect the macros
    """
    
    def __init__(self, folder_list):
        """Initializes the MacroCollection object. """
        
        self.PotentialMacroFiles = []
        
        self.collection = {}
        
        for folder in folder_list:
            
            # Yes for every folder in the list...
            
            folder = folder.strip()
            
            # TODO: if this is to be used on let's say an inferior operating system, this has to be adapted...
            if folder[-1] != '/':
                folder.append('/*.xml')
            else:
                folder.append('*.xml')
            
            # add the macro files to our list of files...
             
            self.PotentialMacroFiles.extend( glob.glob(folder) )
            
        
        # OK go through the potential macro files and make macro objects out
        # of them.
        
        for PotentialMacroFile in self.PotentialMacroFiles:
            
            macro = None
            
            try:
                macro = xml_macro( PotentialMacroFile )
            except:
                pass
            else:
                macro.name

    
    
class wakeup_macro( threading.Thread ):
    """This is a macro that can be started and be self maintained.
    It feeds the command queue in the controller with commands until the macro
    completes.
    
    Attribute:
        unit_id -- The specific dimmer that should be used for this wakeup sequence.
    """
    
    def __init__( self, unit_id ):
        """Initialize the wakeup macro. """
        
        threading.Thread.__init__(self)
        self.unit_id = unit_id
        
        
        
    def run(self):
        """This is where the magic happens! """
        
        dim_value = 0
        
        print time.asctime()
        print "wakeup macro for unit %d started" % self.unit_id
        
        while dim_value < 255:
            if dim_value < 10:
                dim_value += 1
            elif dim_value <20:
                dim_value += 2
            else:
                dim_value += 5
            
            
            if dim_value > 255:
                dim_value = 255
                
            # Create the command!
            
            cmd = Telldus.Controller.TelldusCommand( "dim::%d:%d:" % (self.unit_id, dim_value) , False )
            
            # enqueue a command that sets the level on a lamp, this is later
            # received by the Telldus Controller
            
            Telldus.Controller.CommandQueue.put( cmd )
            
            # Sleep for a while so we don't ramp up the lux level to quick
            
            time.sleep( 10 )
        
        print time.asctime()
        print "wakeup macro for unit %d completed" % self.unit_id
        


class xml_macro( threading.Thread ):
    """This is a xml macro that reads a file and then executes it.
    
    Attribute:
        unit_id -- The specific dimmer that should be used for this wakeup sequence.
    """
    
    def __init__( self, macro_file_path ):
        """Initialize the wakeup macro. """
        
        threading.Thread.__init__(self)
#        print os.getcwd()
        self.macroObjects = MacroParser.Macro( macro_file_path )
        
        
        
    def run(self):
        """This is where the magic happens! """
        
        self.macroObjects.execute() 
            
        
        