#!/usr/bin/python

from ctypes import *
import time

"""This is a wrapper for the Telldus Tellstick  core library.
It enables you to use the available remote units as simple objects.
"""


telldus = CDLL( "libtelldus-core.so.2" )

# Callbacks

# http://python.net/crew/theller/ctypes/tutorial.html#callback-functions


#typedef void (WINAPI *TDDeviceEvent)(int deviceId, int method, const char *data, int callbackId, void *context);
TDDEVICEEVENT = CFUNCTYPE( None, c_int, c_int, c_char_p, c_int, c_void_p )
#typedef void (WINAPI *TDDeviceChangeEvent)(int deviceId, int changeEvent, int changeType, int callbackId, void *context); 
TDDEVICECHANGEEVENT = CFUNCTYPE( None, c_int, c_int, c_int, c_int, c_void_p )
#typedef void (WINAPI *TDRawDeviceEvent)(const char *data, int controllerId, int callbackId, void *context);
TDRAWDEVICEEVENT = CFUNCTYPE( None, c_char_p, c_int, c_int, c_void_p )



#TELLSTICK_API void WINAPI tdInit(void);
telldus.tdInit.restype = None
tdInit = telldus.tdInit

#TELLSTICK_API int WINAPI tdRegisterDeviceEvent( TDDeviceEvent eventFunction, void *context );
telldus.tdRegisterDeviceEvent.argtypes = [ TDDEVICEEVENT, c_void_p ]
telldus.tdRegisterDeviceEvent.restype = c_int
tdRegisterDeviceEvent = telldus.tdRegisterDeviceEvent

#TELLSTICK_API int WINAPI tdRegisterDeviceChangeEvent( TDDeviceChangeEvent eventFunction, void *context);
telldus.tdRegisterDeviceChangeEvent.argtypes = [ TDDEVICECHANGEEVENT, c_void_p ]
telldus.tdRegisterDeviceChangeEvent.restype = c_int
tdRegisterDeviceChangeEvent = telldus.tdRegisterDeviceChangeEvent

#TELLSTICK_API int WINAPI tdRegisterRawDeviceEvent( TDRawDeviceEvent eventFunction, void *context );
telldus.tdRegisterRawDeviceEvent.argtypes = [ TDRAWDEVICEEVENT, c_void_p ]
telldus.tdRegisterRawDeviceEvent.restype = c_int
tdRegisterRawDeviceEvent = telldus.tdRegisterRawDeviceEvent

#TELLSTICK_API int WINAPI tdUnregisterCallback( int callbackId );
telldus.tdUnregisterCallback.argtypes = [c_int ]
telldus.tdUnregisterCallback.restype = c_int
tdUnregisterCallback = telldus.tdUnregisterCallback

#TELLSTICK_API void WINAPI tdClose(void);
telldus.tdClose.restype = None
tdClose = telldus.tdClose



#TELLSTICK_API void WINAPI tdReleaseString(char *string);
telldus.tdReleaseString.argtypes = [ c_char_p ];
telldus.tdReleaseString.restype = None

#TELLSTICK_API int WINAPI tdTurnOn(int intDeviceId);
telldus.tdTurnOn.argtypes = [ c_int ]
telldus.tdTurnOn.restype = c_int
tdTurnOn = telldus.tdTurnOn

#TELLSTICK_API int WINAPI tdTurnOff(int intDeviceId);
telldus.tdTurnOff.argtypes = [ c_int ]
telldus.tdTurnOff.restype = c_int
tdTurnOff = telldus.tdTurnOff

#TELLSTICK_API int WINAPI tdBell(int intDeviceId);
telldus.tdBell.argtypes = [ c_int ]
telldus.tdBell.restype = c_int
tdBell = telldus.tdBell

#TELLSTICK_API int WINAPI tdDim(int intDeviceId, unsigned char level);
telldus.tdDim.argtypes = [ c_int, c_ubyte ]
telldus.tdDim.restype = c_int
tdDim = telldus.tdDim
#TELLSTICK_API int WINAPI tdLearn(int intDeviceId);
telldus.tdLearn.argtypes = [ c_int ]
telldus.tdLearn.restype = c_int
tdLearn = telldus.tdLearn
#TELLSTICK_API int WINAPI tdMethods(int id, int methodsSupported);
telldus.tdMethods.argtypes = [ c_int, c_int ]
telldus.tdMethods.restype = c_int
tdMethods = telldus.tdMethods
#TELLSTICK_API int WINAPI tdLastSentCommand( int intDeviceId, int methodsSupported );
telldus.tdLastSentCommand.argtypes = [ c_int, c_int ]
telldus.tdLastSentCommand.restype = c_int
tdLastSentCommand = telldus.tdLastSentCommand
#TELLSTICK_API char *WINAPI tdLastSentValue( int intDeviceId );
telldus.tdLastSentValue.argtypes = [ c_int ]
telldus.tdLastSentValue.restype = c_char_p
tdLastSentValue = telldus.tdLastSentValue

#TELLSTICK_API int WINAPI tdGetNumberOfDevices();
#telldus.tdGetNumberOfDevices.argtypes = [ None ]
telldus.tdGetNumberOfDevices.restype = c_int
tdGetNumberOfDevices = telldus.tdGetNumberOfDevices
#TELLSTICK_API int WINAPI tdGetDeviceId(int intDeviceIndex);
telldus.tdGetDeviceId.argtypes = [ c_int ]
telldus.tdGetDeviceId.restype = c_int
tdGetDeviceId = telldus.tdGetDeviceId

#TELLSTICK_API int WINAPI tdGetDeviceType(int intDeviceId);
telldus.tdGetDeviceType.argtypes = [ c_int ]
telldus.tdGetDeviceType.restype = c_int
tdGetDeviceType = telldus.tdGetDeviceType

#TELLSTICK_API char * WINAPI tdGetErrorString(int intErrorNo);
telldus.tdGetErrorString.argtypes = [ c_int ]
telldus.tdGetErrorString.restype = c_char_p
tdGetErrorString = telldus.tdGetErrorString

#TELLSTICK_API char * WINAPI tdGetName(int intDeviceId);
telldus.tdGetName.argtypes = [ c_int ]
telldus.tdGetName.restype = c_char_p
tdGetName = telldus.tdGetName

#TELLSTICK_API bool WINAPI tdSetName(int intDeviceId, const char* chNewName);
telldus.tdSetName.argtypes = [ c_int, c_char_p ]
telldus.tdSetName.restype = c_int
tdSetName = telldus.tdSetName

#TELLSTICK_API char * WINAPI tdGetProtocol(int intDeviceId);
telldus.tdGetProtocol.argtypes = [ c_int ]
telldus.tdGetProtocol.restype = c_char_p
tdGetProtocol = telldus.tdGetProtocol

#TELLSTICK_API bool WINAPI tdSetProtocol(int intDeviceId, const char* strProtocol);
telldus.tdSetProtocol.argtypes = [ c_int, c_char_p ]
telldus.tdSetProtocol.restype = c_int
tdSetProtocol = telldus.tdSetProtocol

#TELLSTICK_API char * WINAPI tdGetModel(int intDeviceId);
telldus.tdGetModel.argtypes = [ c_int ]
telldus.tdGetModel.restype = c_char_p
tdGetModel = telldus.tdGetModel

#TELLSTICK_API bool WINAPI tdSetModel(int intDeviceId, const char *intModel);
telldus.tdSetModel.argtypes = [ c_int, c_char_p ]
telldus.tdSetModel.restype = c_int
tdSetModel = telldus.tdSetModel

#TELLSTICK_API char * WINAPI tdGetDeviceParameter(int intDeviceId, const char *strName, const char *defaultValue);
telldus.tdGetDeviceParameter.argtypes = [ c_int, c_char_p, c_char_p ]
telldus.tdGetDeviceParameter.restype = c_char_p
tdGetDeviceParameter = telldus.tdGetDeviceParameter

#TELLSTICK_API bool WINAPI tdSetDeviceParameter(int intDeviceId, const char *strName, const char* strValue);
telldus.tdSetDeviceParameter.argtypes = [ c_int, c_char_p, c_char_p ]
telldus.tdSetDeviceParameter.restype = c_int
tdSetDeviceParameter = telldus.tdSetDeviceParameter

#TELLSTICK_API int WINAPI tdAddDevice();
#telldus.tdAddDevice.argtypes = [ None ]
telldus.tdAddDevice.restype = c_int
tdAddDevice = telldus.tdAddDevice

#TELLSTICK_API bool WINAPI tdRemoveDevice(int intDeviceId);
telldus.tdRemoveDevice.argtypes = [ c_int ]
telldus.tdRemoveDevice.restype = c_int
tdRemoveDevice = telldus.tdRemoveDevice

#TELLSTICK_API int WINAPI tdSendRawCommand(const char *command, int reserved);
telldus.tdSendRawCommand.argtypes = [ c_char_p, c_int ]
telldus.tdSendRawCommand.restype = c_int
tdSendRawCommand = telldus.tdSendRawCommand

#TELLSTICK_API void WINAPI tdConnectTellStickController(int vid, int pid, const char *serial);
telldus.tdConnectTellStickController.argtypes = [ c_int, c_int, c_char_p ]
telldus.tdConnectTellStickController.restype = None
tdConnectTellStickController = telldus.tdConnectTellStickController

#TELLSTICK_API void WINAPI tdDisconnectTellStickController(int vid, int pid, const char *serial);
telldus.tdDisconnectTellStickController.argtypes = [ c_int, c_int, c_char_p ]
telldus.tdDisconnectTellStickController.restype = None
tdDisconnectTellStickController = telldus.tdDisconnectTellStickController


# Device Methods
TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_BELL = 4
TELLSTICK_TOGGLE = 8
TELLSTICK_DIM = 16
TELLSTICK_LEARN = 32

# Error codes
TELLSTICK_SUCCESS = 0
TELLSTICK_ERROR_NOT_FOUND = -1
TELLSTICK_ERROR_PERMISSION_DENIED = -2
TELLSTICK_ERROR_DEVICE_NOT_FOUND = -3
TELLSTICK_ERROR_METHOD_NOT_SUPPORTED = -4
TELLSTICK_ERROR_COMMUNICATION = -5
TELLSTICK_ERROR_CONNECTING_SERVICE = -6
TELLSTICK_ERROR_UNKNOWN_RESPONSE = -7
TELLSTICK_ERROR_UNKNOWN = -99

# Device typedef
TELLSTICK_TYPE_DEVICE = 1
TELLSTICK_TYPE_GROUP = 2

# Device changes
TELLSTICK_DEVICE_ADDED = 1
TELLSTICK_DEVICE_CHANGED = 2
TELLSTICK_DEVICE_REMOVED = 3
TELLSTICK_DEVICE_STATE_CHANGED = 4

# Change types
TELLSTICK_CHANGE_NAME = 1
TELLSTICK_CHANGE_PROTOCOL = 2
TELLSTICK_CHANGE_MODEL = 3

# Protocol Nexa
TELLSTICK_DEVICE_YCR3500 = 1
TELLSTICK_DEVICE_YCR300D = 2
TELLSTICK_DEVICE_WSR1000 = 3
TELLSTICK_DEVICE_CMR1000 = 4
TELLSTICK_DEVICE_CMR300 = 5
TELLSTICK_DEVICE_PA33300 = 6
TELLSTICK_DEVICE_EL2000 = 8
TELLSTICK_DEVICE_EL2005 = 9
TELLSTICK_DEVICE_EL2006 = 10
TELLSTICK_DEVICE_SYCR3500 = 12
TELLSTICK_DEVICE_SYCR300 = 13
TELLSTICK_DEVICE_HDR105 = 14
TELLSTICK_DEVICE_ML7100 = 15
TELLSTICK_DEVICE_EL2004 = 16
TELLSTICK_DEVICE_EL2016 = 17
TELLSTICK_DEVICE_EL2010 = 18
TELLSTICK_DEVICE_LYCR1000 = 20
TELLSTICK_DEVICE_LYCR300 = 21
TELLSTICK_DEVICE_LCMR1000 = 22
TELLSTICK_DEVICE_LCMR300 = 23
TELLSTICK_DEVICE_EL2023 = 24
TELLSTICK_DEVICE_EL2024 = 25
TELLSTICK_DEVICE_EL2021 = 26
TELLSTICK_DEVICE_EL2017 = 27
TELLSTICK_DEVICE_EL2019 = 28

# Protocol Ikea
TELLSTICK_DEVICE_KOPPLA = 19


class remote_unit( object ):

    """
    This is a generic lamp object.
    
    it has a position an id and a description
    """

    def __init__( self, position, id, description ):

        """Initializes the object and assigns the values to the attributes
        
        Attributes:
            position      -- the position in array when retrieved
            id            -- the id of the lamp
            description   -- the Description of the lamp
        """

        self.position = position
        self.id = id
        self.description = description



    def value( self ):

        """Retrieves the last sent value for the unit. """

        state = telldus.tdLastSentCommand( self.id, TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_DIM )

        if state & TELLSTICK_TURNON:

            dim_level = 255

        elif state & TELLSTICK_TURNOFF:

            dim_level = 0

        elif state & TELLSTICK_DIM:

            dim_level = int( telldus.tdLastSentValue( self.id ) )

        return dim_level



class switch( remote_unit ):

    """This is a representation of an on/off switch. """

    ON = 1
    OFF = 0

    type = "SWITCH"


    def switch( self, state ):
        """This method either turns the lamp on or off depending on the given
            state.
            
        Attribute:
            state    -- The state of the lamp that should be set
        """

        if state == switch.OFF:
            telldus.tdTurnOff( self.id )
        elif state == switch.ON:
            telldus.tdTurnOn( self.id )
        else:
            raise ValueError( "Not a valid Value" )

        return state




class dimmer( switch ):

    """This is a representation of a dimmer switch. """

    type = "DIMMER"

    def dim( self, value ):
        """Dims the lamp to a specific value.
        
        Attribute:
            value   -- A value between 0 and 255.
            
        Returns:
            The current value.
        """
        if value > 0 and value < 255:
            telldus.tdDim( self.id, value )
        elif value == 0:
            telldus.tdTurnOff( self.id )
        else:
            telldus.tdDim( self.id, 255 )

        return value



    def step( self, value ):
        """Dims the lamp with the specific value.
        
        Attribute:
            value   -- A value between -255 and 255.
            
        Returns:
            The current value.
        """


        # Retrieve the last sent command

        state = telldus.tdLastSentCommand( self.id, TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_DIM )

        if state & TELLSTICK_TURNON:

            dim_level = 255

        elif state & TELLSTICK_TURNOFF:

            dim_level = 0

        elif state & TELLSTICK_DIM:

            dim_level = int( telldus.tdLastSentValue( self.id ) )


        value += dim_level

        if value > 255:
            value = 255
        elif value < 0:
            value = 0

        telldus.tdDim( self.id, value )

        return value



class bell( remote_unit ):

    """This is a representation of a bell. """


    type = "BELL"

    def ring( self ):

        """Rings the bell... """

        telldus.tdBell( self.id )



def generate():

    """Retrieves and generates a list of objects representing the available
     remote units.
    """

    switches = {}

    for i in range( telldus.tdGetNumberOfDevices() ):

        # For every device

        dev_id = telldus.tdGetDeviceId( i )
        dev_name = telldus.tdGetName( dev_id )
        dev_model = telldus.tdGetModel( dev_id )

        if dev_model == "codeswitch":

            switches[dev_id] = switch( i, dev_id, dev_name )

        if dev_model == "selflearning-switch":

            switches[dev_id] = switch( i, dev_id, dev_name )

        elif dev_model == "selflearning-dimmer":

            switches[dev_id] = dimmer( i, dev_id, dev_name )

        elif dev_model == "bell":

            switches[dev_id] = bell( i, dev_id, dev_name )

        else:

            switches[dev_id] = switch( i, dev_id, dev_name )

        #switches[dev_name] = switches[dev_id]

    return switches



if __name__ == '__main__':

    # This is just for testing the library, probably with all likeliness needs
    # adjusting for your setup

    switches = generate()

    #print switches["Living Room"].step( -200 )
    print switches[2].step( 100 )

    #print switches["Water Kettle Kitchen"].step( -20 )

    time.sleep( 5 )

    switches["Living Room"].switch( switch.ON )

