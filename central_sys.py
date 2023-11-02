import asyncio
import logging
from datetime import datetime, timedelta
import random 

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus
from ocpp.v16 import call_result
from ocpp.v16.datatypes import IdTagInfo

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

   @on(Action.Authorize)
   def on_authorize(self, id_tag:str, **kwargs):
     id_tag_info = IdTagInfo(
        status=AuthorizationStatus.accepted,
        expiry_date=(datetime.now() + timedelta(days=30)).isoformat(),
        parent_id_tag="AA1234"
    )
     return call_result.AuthorizePayload(id_tag_info.__dict__) 
       


   @on(Action.BootNotification)
   def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )

    
   @on('Heartbeat')
   def on_heartbeat(self):
       print('Got a Heartbeat!')
       return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
            
        )
   


   


   @on(Action.StartTransaction)
   def on_start_transaction(self,connector_id, id_tag, timestamp, meter_start, reservation_id):
         
        
         return call_result.StartTransactionPayload(  id_tag_info={ 'status':AuthorizationStatus.accepted, 'expiry_date':(datetime.now() + timedelta(days=30)).isoformat(), 'parent_id_tag':"AA1234"},      transaction_id=int(1))



   @on('MeterValues')
   def on_meter_values(self, connector_id, meter_value, transaction_id):
         return call_result.MeterValuesPayload() 



   @on(Action.StopTransaction)
   def on_stop_transaction(self, meter_stop, timestamp, transaction_id, reason, id_tag, transaction_data):
    
          return call_result.StopTransactionPayload( id_tag_info={ 'status':AuthorizationStatus.accepted, 'expiry_date':(datetime.now() + timedelta(days=30)).isoformat(), 'parent_id_tag':"AA1234"} )
    


   



async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.error(
            "Client hasn't requested any Subprotocol. Closing Connection"
        )
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()



    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()
    



async def main():


    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()





if __name__ == "__main__":
    

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
