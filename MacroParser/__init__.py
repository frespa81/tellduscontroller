#!/usr/bin/python

import xml.parsers.expat
import time
import Telldus.Controller
import threading



class Macro( object ):
    """This is a macro object it parses and executes a xml macro. """

    def __init__( self, macroFilePath ):
        """Initialize the macro object.
        
        Attributes:
        
        macroFilePath - The path to the xml file
        """

        self.xmlfile = open( macroFilePath, 'r' )

        self.parser = xml.parsers.expat.ParserCreate()

        self.parser.StartElementHandler = self.start_element
        self.parser.CharacterDataHandler = self.char_data
        self.parser.EndElementHandler = self.end_element

        self.MacroHandle = None

        self.forks = []

        self._parse()



    def _parse( self ):
        """Begin parsing the xml file. """

        self.parser.ParseFile( self.xmlfile )



    def start_element( self, name, attrs ):
        """ This is a handle method used to handle the requests from the parser. """

        # Create our new macrotag_object

        self.MacroHandle = globals()[ "macrotag_" + name ]( attrs, self )

        # Assign the handlers to the mTag object

        self.parser.StartElementHandler = self.MacroHandle.start_element
        self.parser.CharacterDataHandler = self.MacroHandle.char_data
        self.parser.EndElementHandler = self.MacroHandle.end_element



    def char_data( self ):
        """ This is a handle method used to handle the requests from the parser. """
        pass



    def end_element( self ):
        """ This is a handle method used to handle the requests from the parser. """
        pass



    def execute( self ):
        """This method executes the macro. """

        self.MacroHandle.execute()

        while len( self.forks ):

            # There are at least one fork left that we should wait for to finish

            self.forks[0].join()

            # remove the fork from the list

            del( self.forks[0] )



class ForkContainer( threading.Thread ):
    """This is just a simple container for a forked object. """

    def __init__( self, children, TraverseTree=True ):

        threading.Thread.__init__( self )

        self.children = children
        self.TraverseTree = TraverseTree

    def run( self ):
        """Start the thread. """

        if self.TraverseTree:

            # Call all child objects and let them do what they are
            # supposed to do...

            for child in self.children:

                # For every child execute

                child.execute( self.TraverseTree )




class macrotag_common( object ):
    """This is a least common denominator for all tags in a macro xml file. """

    def __init__( self, attributes={}, parent=None ):
        """Initializes the object. 
        
        Attributes:
        attributes - the attributes from the xml tag.
        parent     - the parent object.
        parser     - the parser object.
        """

        self._attributes = attributes
        self._children = []
        self.parent = parent
        self.parser = parent.parser
        self.forks = parent.forks
        self.text = ""

        self._verify()



    def _verify( self ):
        """This method should be inherited and used when verifying mandatory
        attributes. """
        pass



    def __getattr__( self, name ):

        if name == "lastChild":
            return self._children[-1]
        elif name == "firstChild":
            return self._children[0]
        else:
            raise AttributeError()



    def append( self, child ):
        """Add a child to the list of children. """

        self._children.append( child )



    def execute( self, TraverseTree=True ):
        """ This is a generic execute method, this should be implemented in
        all the objects inheriting from this object. """

        # Do what the object is supposed to do...

        self._doTask()

        if len( self.forks ):

            # There are forked threads make the queuing fair, This is a hack...
            # The tiny sleep gives the sibling threads time to enqueue their commands

            time.sleep( 0.1 )

        if TraverseTree:

            # Call all child objects and let them do what they are
            # supposed to do...

            for child in self._children:

                # For every child execute

                child.execute( TraverseTree )

        self._doCleanUp()



    def _doTask( self ):
        """All inheriting objects must implement this method if they should do
        a task. This is where the stuff happens... """
        pass



    def _doCleanUp( self ):
        """If there needs to be anything done after a task, i.e. cleanup """
        pass



    def start_element( self, name, attrs ):
        """ This is a handle method used to handle the requests from the parser. """

        # Create our new macrotag_object

        mTag = globals()[ "macrotag_" + name ]( attrs, self )

        # Welcome mTag among our children

        self.append( mTag )

        # Assign the handlers to the mTag object

        self.parser.StartElementHandler = mTag.start_element
        self.parser.CharacterDataHandler = mTag.char_data
        self.parser.EndElementHandler = mTag.end_element




    def end_element( self, name ):
        """ This is a handle method used to handle the requests from the parser. """

        self.parser.StartElementHandler = self.parent.start_element
        self.parser.CharacterDataHandler = self.parent.char_data
        self.parser.EndElementHandler = self.parent.end_element



    def char_data( self, data ):
        """ This is a handle method used to handle the requests from the
        parser.
        """

        self.text += data



class macrotag_macro( macrotag_common ):
    """This is the root of all that is macro... """

    def _verify( self ):
        """Verify the attributes. """

        if "name" not in self._attributes:
            raise MissingAttributeError( "There is no 'name' attribute." )



    def _beginDoTask( self ):
        """Doesn't do much, can't really do anything... """
        pass





class macrotag_loop( macrotag_common ):
    """This is a loop tag."""

    def _verify( self ):

        if "iterations" in self._attributes:
            self._attributes["iterations"] = int( self._attributes["iterations"] )
        else:
            raise MissingAttributeError( "iterations is missing" )

        self.loop_count = None




    def execute( self, TraverseTree=True ):
        """ This is a generic execute method, thi should be implemented in
        all the objects inheriting from this object. """

        # Do what the object is supposed to do... 
        self.loop_count = self._attributes["iterations"]

        while self.loop_count:

            if TraverseTree:

                # Call all child objects and let them do what they are
                # supposed to do...

                for child in self._children:

                    # For every child execute

                    child.execute( TraverseTree=True )

            self.loop_count -= 1

        self._doCleanUp()




class macrotag_sleep( macrotag_common ):
    """This is a sleep tag."""

    def _verify( self ):

        if "time" in self._attributes:
            self._attributes["time"] = float( self._attributes["time"] )
        else:
            raise MissingAttributeError( "time is missing" )



    def _doTask( self ):
        """Sleeps for a given time... """

        time.sleep( self._attributes['time'] )



class macrotag_fork( macrotag_common ):
    """This is a fork tag it executes all child elements in a separate parallel
    thread.
    """

    def _verify( self ):

        if "delay" in self._attributes:
            self._attributes["delay"] = float( self._attributes["delay"] )



    def execute( self, TraverseTree=True ):
        """ Creates the fork thread and passes the child objects to the thread
        they in turn are executed in parallel with the sibling objects."""

        fork = ForkContainer( self._children, TraverseTree )

        fork.start()

        self.forks.append( fork )

        self._doCleanUp()



class macrotag_print( macrotag_common ):
    """This is a print tag."""

    def _verify( self ):

        if "text" not in self._attributes:
            raise MissingAttributeError( "text is missing" )



    def _doTask( self ):
        """Doesn't do much, can't really do anything... """

        print self._attributes['text']



class macrotag_switch( macrotag_common ):
    """This is a switch tag."""

    def _verify( self ):

        if "unit_id" not in self._attributes:
            raise MissingAttributeError( "unit_id is missing" )

        if "state" not in self._attributes:
            raise MissingAttributeError( "state is missing" )

        if self._attributes["state"] not in ["0", "1"]:
            raise InvalidAttributeValueError( "no valid value" )



    def _doTask( self ):
        """Creates the switch command and enqueues it... """

        # Create the command!

        cmd = Telldus.Controller.TelldusCommand( "switch::%s:%s:" % \
                                                 ( self._attributes["unit_id"], \
                                                  self._attributes["state"] ), \
                                                  False )

        # enqueue a command that sets the level on a lamp, this is later
        # received by the Telldus Controller

        Telldus.Controller.CommandQueue.put( cmd )




class macrotag_step( macrotag_common ):
    """This is a dim tag."""

    def _verify( self ):

        if "unit_id" not in self._attributes:
            raise MissingAttributeError( "unit_id is missing" )

        if "value" in self._attributes:
            self._attributes["value"] = int( self._attributes["value"] )
        else:
            raise MissingAttributeError( "value is missing" )

        if self._attributes["value"] > 255 or self._attributes["value"] < -255:
            raise InvalidAttributeValueError( "no valid value" )




    def _doTask( self ):
        """Creates the switch command and enqueues it... """

        # Create the command!

        cmd = Telldus.Controller.TelldusCommand( "step::%s:%s:" % \
                                                 ( self._attributes["unit_id"], \
                                                  self._attributes["value"] ), \
                                                  False )

        # enqueue a command that sets the level on a lamp, this is later
        # received by the Telldus Controller

        Telldus.Controller.CommandQueue.put( cmd )




class macrotag_dim( macrotag_common ):
    """This is a dim tag."""

    def _verify( self ):

        if "unit_id" not in self._attributes:
            raise MissingAttributeError( "unit_id is missing" )

        if "value" in self._attributes:
            self._attributes["value"] = int( self._attributes["value"] )
        else:
            raise MissingAttributeError( "value is missing" )

        if self._attributes["value"] > 255 or self._attributes["value"] < 0:
            raise InvalidAttributeValueError( "no valid value" )



    def _doTask( self ):
        """Creates the switch command and enqueues it... """

        # Create the command!

        cmd = Telldus.Controller.TelldusCommand( "dim::%s:%s:" % \
                                                 ( self._attributes["unit_id"], \
                                                  self._attributes["value"] ), \
                                                  False )

        # enqueue a command that sets the level on a lamp, this is later
        # received by the Telldus Controller

        Telldus.Controller.CommandQueue.put( cmd )



class macrotag_bell( macrotag_common ):
    """This is a bell tag."""

    def _verify( self ):

        if "unit_id" not in self._attributes:
            raise MissingAttributeError( "unit_id is missing" )



    def _doTask( self ):
        """Creates the ring command and enqueues it... """

        # Create the command!

        cmd = Telldus.Controller.TelldusCommand( "bell::%s:0:" % \
                                                 self._attributes["unit_id"], \
                                                 False )

        # enqueue a command that sets the level on a lamp, this is later
        # received by the Telldus Controller

        Telldus.Controller.CommandQueue.put( cmd )



class MissingAttributeError( Exception ):
    """This should be raised if there are a missing attribute. """

    def __init__( self, value ):
        """Initialize the generic macro error. """
        self.value = value



    def __str__( self ):
        return repr( self.value )



class InvalidAttributeValueError( Exception ):
    """This should be raised if there are a missing attribute. """

    def __init__( self, value ):
        """Initialize the generic macro error. """
        self.value = value



    def __str__( self ):
        return repr( self.value )



if __name__ == '__main__':
    """ This is just for testing """

    m = Macro( "macro.xml" )

    m.execute()
