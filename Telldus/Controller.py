#!/usr/bin/python


import Telldus
import threading
import Queue
import re
import hashlib
import json


SECRET_KEY = 'APA'

CommandQueue = Queue.Queue() # This is a static queue, and it's thread safe
ResponseQueue = Queue.Queue() # This is a static queue, and it's thread safe


class InvalidCommandError( Exception ):
    """Generic Error that should be raised when a command error is detected. """

    def __init__( self, value ):
        """Initialize the Generic Command error object. """

        self.value = value


    def __str__( self ):
        return repr( self.value )



class AuthenticationError( Exception ):
    """Authentication Error that should be raised when a command Authentication
    failure is detected. """

    def __init__( self, value ):
        """Initialize the Authentication error object. """
        self.value = value


    def __str__( self ):
        return repr( self.value )



class InvalidMacroError( Exception ):
    """Generic Error that should be raised when trying to call an invalid macro. """

    def __init__( self, value ):
        """Initialize the generic macro error. """
        self.value = value


    def __str__( self ):
        return repr( self.value )



class TelldusCommand( object ):
    """This is a command object used to parse and hold a command that should be 
    processed by the controller.
    
    Attributes:
        data -- The data from the TCP connection that should be parsed.
                The data should be formated according to the following example.
                
                <command>:<macro>:<unitid>:<value>:<hash>
                
        authenticate -- True if the command data should be authenticated. If
                        there should be no authentication then replace <hash>
                        with a 0 
    """

    def __init__( self, data, authenticate=True ):
        """Initialize the TelldusCommand object. """

        self.result = None
        self.command = None
        self.macro = None
        self.unit_id = None
        self.value = None
        self.hash = None

        # Create the event_lock used for this command object

        self.event_lock = threading.Event()

        # verify the data and eventually the hash

        self.Parse( data, authenticate )

        self.Verify()


    def Parse( self, data, authenticate ):
        """Parse the command data and hash. """

        try:
            ( self.command,
             self.macro,
             self.unit_id,
             self.value,
             self.hash ) = data.split( ':' )
        except ValueError:
            raise InvalidCommandError( "Could not parse the command data, malformed data." )


        if authenticate:

            # Yes this command should be validated

            if not re.match( "^[0-9a-fA-F]{40}$", self.hash ):
                raise InvalidCommandError( "Could not parse the command data, malformed hashsum." )


    def Verify( self ):
        """Verify the command. """

        if self.command not in ["step", "dim", "switch", "bell", "macro", "state", "list"]:
            raise InvalidCommandError( "Could not parse the command data, invalid command type." )

        if self.command == "macro": # FIXME: make sure we have a way of checking if the macro exists
            if self.macro not in ["wakeup", "xml"]:
                raise InvalidCommandError( "Could not parse the command data, invalid macro." )
        else:
            try:
                self.unit_id = int( self.unit_id )
            except ValueError:
                raise InvalidCommandError( "Could not parse the command data, invalid unit_id." )
            try:
                self.value = int( self.value )
            except ValueError:
                raise InvalidCommandError( "Could not parse the command data, invalid value." )

            if self.command == "step":
                if self.value < -255 or self.value > 255:
                    raise InvalidCommandError( "Could not parse the command data, value out of range." )

            if self.command == "dim":
                if self.value < 0 or self.value > 255:
                    raise InvalidCommandError( "Could not parse the command data, value out of range.( %d )" & self.value )

            if self.command == "switch":
                if self.value < 0 or self.value > 1:
                    raise InvalidCommandError( "Could not parse the command data, value out of range." )



class TelldusJSONCommand( TelldusCommand ):
    """This is a command object used to parse a JSON string and hold a command
    that should be processed by the controller.
    
    Attributes:
        data -- The data from the TCP connection that should be parsed.
                The data should be formated according to the following example.
                
                { "command":"dim",
                  "unit_id":"1",
                  "value":"200",
                  "hash":"1234567890123456789012345678901234567890" }
                  
                
                
        authenticate -- True if the command data should be authenticated. If
                        there should be no authentication then replace <hash>
                        with a 0 
    """

    def Authenticate( self, obj ):
        """Authenticate the JSON command object.
        
        Attribute:
        obj -- The JSON object representing the command. """

        # We should verify the command...
        # replace the hash with the secret key

        self.hash = obj["hash"]
        obj["hash"] = SECRET_KEY

        # Format the data so we can calculate the object hash 

        if self.Hash().lower() == self.hash.lower():

            # the command is authentic

            return True

        else:

            # the command is not authentic

            return False


    def Hash( self ):
        """Calculates the hash for the object. """

        hashString = str( self.command ) + str( self.macro ) + str( self.result ) + \
                        SECRET_KEY + str( self.unit_id ) + str( self.value )

        return hashlib.sha1( hashString ).hexdigest()


    def Parse( self, data, authenticate ):
        """Verify and parse the command data and hash. """
        #print '"'+ data +'"' 
        obj = json.loads( data )

        try:

            # Assign the values

            self.command = obj["command"]

            if "macro" in obj.keys():
                self.macro = obj["macro"]

            self.unit_id = obj["unit_id"]
            self.value = obj["value"]

        except:
            raise InvalidCommandError( "Could not parse the command." )

        if authenticate:

            if not self.Authenticate( obj ):

                raise AuthenticationError( "Could not authenticate the command." )


    def __str__( self ):
        """Returns the command in JSON representation. """
        obj = {}

        obj["command"] = self.command
        obj["unit_id"] = self.unit_id
        obj["value"] = self.value
        obj["macro"] = self.macro
        obj["result"] = self.result
        obj["hash"] = self.Hash()


        return json.dumps( obj )



class TelldusController( threading.Thread ):
    """This is the controller that handles all the commands aimed for the the
        tellstick device.
    """

    def __init__( self ):
        """Initialize the Telldus Controller. """

        threading.Thread.__init__( self )
        self.should_be_running = True
        self.running_macros = []

        # Get all the current switches from the telldus library

        self.switches = Telldus.generate()


    def run( self ):
        """This method is the telldus controller core, this is where IT happens.
            The method is called when the start() method is called on the thread.
        """

        while self.should_be_running or not CommandQueue.empty():

            # check all the running macros if there are any that is dead if so
            # then remove them from the list.

            for i in range( len( self.running_macros ) ):

                # Go through the list of active macros

                if not self.running_macros[i].isAlive():

                    # a dead thread was found, remove it from the list.

                    del self.running_macros[i]

                    # we have to break here otherwise we will end up with a
                    # Index Error

                    break

            # Check the CommandQueue for a command

            cmd = None

            try:

                # Retrieve a command object, block for 2 seconds
                cmd = CommandQueue.get( True, 2 )

            except Queue.Empty:

                continue

            else:

                # Handle the Command

                if cmd.command == "dim":

                    # This is a dim command

                    cmd.result = self.switches[cmd.unit_id].dim( cmd.value )

                elif cmd.command == "switch":

                    # This is a switch command

                    cmd.result = self.switches[cmd.unit_id].switch( cmd.value )

                elif cmd.command == "step":

                    # this is a step command

                    cmd.result = self.switches[cmd.unit_id].step( cmd.value )

                elif cmd.command == "bell":

                    # this is a bell command

                    cmd.result = self.switches[cmd.unit_id].ring()

                elif cmd.command == "macro":

                    # This is a macro command, let's create and start
                    # the specific macro thread.


                    try:
                        _tmp = __import__( 'MacroParser.Macros', globals(),
                                           locals(), [cmd.macro + '_macro'] )


                        macro_class = getattr( _tmp, "%s_macro" % cmd.macro )
                        macro_thread = macro_class( cmd.unit_id )

                    except:

                        # We should not end up here...
                        # The command parser should have made sure of this...

                        raise InvalidMacroError( "There where no macro with the name, %s." % str( cmd.macro ) )

                    # Check the macro_thread, it should be a thread

                    if not isinstance( macro_thread, threading.Thread ):

                        # We should not end up here...
                        # The command parser should have made sure of this...

                        raise InvalidMacroError( "There where no macro with the name, %s" % str( cmd.macro ) )

                    # Start the macro thread

                    macro_thread.start()

                    self.running_macros.append( macro_thread )

                    cmd.result = 1

                elif cmd.command == "state":

                    # This is a state command report the state of the switch

                    cmd.result = self.switches[cmd.unit_id].value()

                elif cmd.command == "list":

                    # This is a list command, return a list of the available switches

                    switch_list = []
                    for key in self.switches.keys():
                        switch_list.append( {"id":self.switches[key].id,
                                     "description":self.switches[key].description,
                                     "type":self.switches[key].type,
                                     "value":self.switches[key].value()} )

                    cmd.result = switch_list

                else:

                    # We should not end up here...
                    # The command parser should have made sure of this...

                    raise InvalidCommandError( "Invalid Command" )


                # Set the event now that we are done with the command.

                cmd.event_lock.set()
