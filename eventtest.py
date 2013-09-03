#!/usr/bin/python

import Telldus
import time

class tddata():
    def __init__( self, stringdata ):
        self._stringdata = stringdata

class test():

    def __init__( self ):

        Telldus.tdInit()

        self.test = 5

        self.DeviceCallback = Telldus.TDDEVICEEVENT( self.cbDevice )
        self.RawDeviceCallback = Telldus.TDRAWDEVICEEVENT( self.cbRawDevice )

        Telldus.tdRegisterDeviceEvent( self.DeviceCallback, self.test )
        Telldus.tdRegisterRawDeviceEvent( self.RawDeviceCallback, self.test )



        for i in range( Telldus.tdGetNumberOfDevices() ):
            print "-" * 40
            dev_id = Telldus.tdGetDeviceId( i )
            dev_name = Telldus.tdGetName( dev_id )
            dev_model = Telldus.tdGetModel( dev_id )
            print dev_id,
            print dev_name,
            print dev_model


    def cbRawDevice( self, data, cid, cbid, context ):
        print time.asctime()
        print "DeviceRawCallback"
        print data
        print cid
        print cbid
        print context


    def cbDevice( self, did, method, stringdata, cbid, context ):
        print time.asctime()
        print "DeviceCallback"
        print did
        print method
        print stringdata
        print cbid
        print context


    def __del__( self ):
        Telldus.tdClose()


    def pr( self ):
        print "hej"





#typedef void (WINAPI *TDRawDeviceEvent)(const char *data, int controllerId, int callbackId, void *context);
#TDRAWDEVICEEVENT = telldus.TDRAWDEVICEEVENT = CFUNCTYPE( c_char_p, c_int, c_int, c_void_p )

t = test()

while( True ):
    time.sleep( 1 )

t.pr()

