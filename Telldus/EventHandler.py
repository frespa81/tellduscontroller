import Queue
import threading
import re
import Telldus
import Controller
import logging.handlers


class ParseRawEventError( Exception ):
    """Error when parsing a raw event."""

    def __init__( self, value ):
        """Initialize the Parse raw event error object. """
        self.value = value


    def __str__( self ):
        return repr( self.value )



class DeviceEvent():
    """A simple representation of a device event."""

    def __init__( self, device_id, method, stringdata, callback_id, context ):

        self.device_id = device_id
        self.method = method
        self.stringdata = stringdata
        self.callback_id = callback_id
        self.context = context


    def __str__( self ):
        print( "DeviceEvent" )
        print( self.device_id )
        print( self.method )
        print( self.stringdata )
        print( self.callback_id )
        print( self.context )
        
            

class RawDeviceEvent():
    """Simple representation of a raw device event."""

    def __init__( self, data, controller_id, callback_id, context ):

        self.data = data

        m = re.match( r"protocol:(.*?);type:(.*?);house:(.*?);group:(.*?);method:(.*?);unit:(.*?);", self.data )

        if m:
            self.protocol = m.group( 1 )
            self.type = m.group( 2 )
            self.house_code = m.group( 3 )
            self.group_code = m.group( 4 )
            self.method = m.group( 5 )
            self.unit = m.group( 6 )
        else:
            raise ParseRawEventError( self.data )

        self.controller_id = controller_id
        self.callback_id = callback_id
        self.context = context
        
        
    def __str__( self ):
        
        print( "RawDeviceEvent" )
        print( self.data )



class EventAction():
    """This is a event action object. """

    def __init__( self, command ):
        """Arguments
        
            command - A TelldusCommand object.
        """

        self.command = command
        self.next = None # This is a reference to another linked Event action. 



class TelldusEventProcessor( threading.Thread ):
    """This is the controller that handles all the incoming events from the
    tellstick duo.
    """

    def __init__( self ):
        """Initialize the Telldus Event Processor. """

        threading.Thread.__init__( self )
        self.abort_thread = threading.Event()

        self.context = 42

        self.event_queue = Queue.Queue()

        # create and register the callback methods

        self._device_callback = Telldus.TDDEVICEEVENT( self.event_callback )
        self._raw_device_callback = Telldus.TDRAWDEVICEEVENT( self.event_raw_callback )
        #self._change_device_callback = Telldus.TDDEVICECHANGEEVENT( self.event_change_callback )

        Telldus.tdRegisterDeviceEvent( self._device_callback, self.context )
        Telldus.tdRegisterRawDeviceEvent( self._raw_device_callback, self.context )
        #Telldus.tdRegisterDeviceChangeEvent( self._change_device_callback, self.context )

        self.action_list = {}


    def event_callback( self, device_id, method, stringdata, callback_id,
                        context ):
        """This event is generated when a already known device is altered. """

        self.event_queue.put( DeviceEvent( device_id, method, stringdata,
                                          callback_id, context ) )


    def event_raw_callback( self, data, controller_id, callback_id, context ):
        """This event is called when a raw unknown signal is detected. """

        self.event_queue.put( RawDeviceEvent( data, controller_id, callback_id,
                                              context ) )


#    def event_change_callback( self, device_id, change_event, change_type,
#                               callback_id, context ):
#        pass


    def run( self ):

        my_logger = logging.getLogger('TeldusLogger')
        my_logger.setLevel(logging.DEBUG)
        handler = logging.handlers.SysLogHandler(address = '/dev/log')
        my_logger.addHandler(handler)

        while not self.abort_thread.isSet():
            EVENT = None

            try:
                EVENT = self.event_queue.get( True, 2.0 )

            except Queue.Empty:
                continue

            # Compare the event against our action list.
            # if there is a match call the function in the action.

            ACTION = None
            try:
                print( "Event:")
                print( EVENT )
                
                my_logger.info(EVENT)
                
                ACTION = self.action_list[EVENT]
                
                Controller.CommandQueue.put( ACTION.command )

                while ACTION.next is not None:
    
                    ACTION = ACTION.next
                    Controller.CommandQueue.put( ACTION.command )
                    
            except IOError as ie:
                raise ie

            except:
                # This event had no action, just log it...
                
                pass

            
