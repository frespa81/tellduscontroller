#!/usr/bin/python

# a simple tcp server

import SocketServer
import random
import hashlib
import time
import socket
import Telldus.Controller as Controller
from Telldus.Controller import SECRET_KEY
import Telldus.EventHandler
import json
import threading
import signal
import sys




"""This is a Telldus Tellstick controller and a TCP server used to control and
give remote network access to the Telldus Controller.
"""


TCP_PORT = 50008

tc_shutdown = False


class TelldusRemoteRequestHandler( SocketServer.BaseRequestHandler ):
    """This is the TCP connection handler. """

    def setup( self ):
        """This method is called when a TCP connection is established. """


        print self.client_address, 'connected!'

        # Send a Token and hash it with the secret key to authenticate ourselves.

        if isinstance( SECRET_KEY, str ):

            # Yes we are to use the SECRET!!!
            token = {}
            token["random"] = str( random.random() )
            token["hash"] = SECRET_KEY
            token["hash"] = hashlib.sha1( token["random"] + token["hash"] ).hexdigest()

            self.request.send( json.dumps( token ) + "\n" )
        else:
            self.request.send( "Hello friend.\n" )



    def handle( self ):
        """When the setup method is done with the connection it is handed over
        to this method. """
        self.request.settimeout( 30.0 )
        data = ""
        while True:
            try:
                data = self.request.recv( 1024 )
            except socket.timeout:
                return


            # verify the date we just got
            print "Received request.",
            print "'" + data + "'"

            # echo the request
            #self.request.send(data)

            if data.strip() == 'bye':

                # This is a request to close the connection

                return

            # Begin parsing what should be a command

            command = None

            try:

                if isinstance( SECRET_KEY, str ):

                    # There is a secret key, use it!

                    command = Controller.TelldusJSONCommand( data.strip(), True )

                else:

                    # There where no secret key, don't authenticate the command

                    command = Controller.TelldusJSONCommand( data.strip(), False )

            except Controller.InvalidCommandError as ice:

                self.request.send( "{\"error\":\"" + str( ice ) + "\"}\n" )

            except Exception as e:

                # This is a catch all, close the connection if this happens

                self.request.send( "{\"error\":\"" + str( e ) + "\"}\n" )

                return


            else:

                Controller.CommandQueue.put( command )

                # Wait for the command to be processed by the controller.

                command.event_lock.wait( 10.0 )

                if command.event_lock.isSet():

                    self.request.send( str ( command ) + "\n" )
                    print( "Request processed." )

                else:

                    self.request.send( "{ \"error\":\"the request timed out.\"}" )
                    print( "Failed to process request." )




    def finish( self ):
        """This is the method that is called when the handle method is done with
        the connection. """
        try:
            self.request.send( 'bye ' + str( self.client_address ) + '\n' )
        except:
            pass
        print self.client_address, 'disconnected!'



    def __del__( self ):
        """This is a cleanup method called when the object gets destroyed. """

        print "Removed thread"

        # Loop on all base classes, and invoke their destructors.
        # Protect against diamond inheritance.

        for base in self.__class__.__bases__:

            # Avoid problems with diamond inheritance.
            basekey = 'del_' + str( base )

            if not hasattr( self, basekey ):

                setattr( self, basekey, 1 )

            else:

                continue

            # Call this base class' destructor if it has one.

            if hasattr( base, "__del__" ):

                base.__del__( self )



class tcserver( threading.Thread ):

    def __init__( self, retries=8 ):

        threading.Thread.__init__( self )
        self.server = None


    def run( self ):
        self.server = SocketServer.ThreadingTCPServer( ( '', TCP_PORT ), TelldusRemoteRequestHandler )
        self.server.serve_forever()


def signal_handler( signal, frame ):
    global tc_shutdown
    tc_shutdown = True



if __name__ == '__main__':

    signal.signal( signal.SIGINT, signal_handler )

    print "Starting the Controller thread...",
    tc = Controller.TelldusController()
    tep = Telldus.EventHandler.TelldusEventProcessor()
    tc.start()
    tep.start()
    print "done."

    print "Starting the Server thread...",
    try:
        server = tcserver()
        server.start()
    except:
        tc.should_be_running = False
        tep.abort_thread.set()
        tep.join()
        tc.join()
        tc_shutdown = True
        print "Could not start the TCP server!"
        sys.exit( 1 )

    print "done."

    while not tc_shutdown:
        time.sleep( 1 )


    print "Shutting down Server thread...",
    server.server.timeout = 0.5
    server.server.shutdown()

    server.join()
    print "done."

    print "Shutting down the Controller thread...",
    tc.should_be_running = False
    tep.abort_thread.set()
    tep.join()
    tc.join()
    print "done."
