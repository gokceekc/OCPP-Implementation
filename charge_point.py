import asyncio
import logging
from datetime import datetime
from typing import List
import subprocess
from websockets import exceptions
import os
import signal

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)


from ocpp.v16 import call
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus,AuthorizationStatus
from ocpp.v16.datatypes import IdTagInfo, MeterValue, SampledValue
from ocpp.v16.enums import ReadingContext, ValueFormat, Measurand, Phase, Location, UnitOfMeasure

logging.basicConfig(level=logging.INFO)

global hb_response



class ChargePoint(cp):
 

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charge_point_model="Optimus",
            charge_point_vendor="The Mobility House"
        )

        response =await self.call(request)
        if response.status == RegistrationStatus.accepted:
            print("Connected to central system.")

        #return response
       

    async def authentication(self):
        request = call.AuthorizePayload(
            id_tag="AA1234")
        response= await self.call(request)
        #print(response)
        #await task1
        #return response
       
       
    async def send_heartbeat(self,interval=10):
        request = call.HeartbeatPayload()
        while True:
            
            hb_response = await self.call(request)
            print("inside the function:", hb_response)
            await asyncio.sleep(interval)
            
           


       
    
    async def start_transaction(self):
         request=call.StartTransactionPayload(connector_id=2, id_tag ="AA1234", meter_start=1, timestamp=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z",
         reservation_id=12)
         
         response= await self.call(request)
         
        

    async def send_meter_value(self):
          

          request= call.MeterValuesPayload(
     meter_value=[{"sampledValue": [{"value": "000", "context": "Sample.Periodic",
                                       "format": "Raw",
                                       "location": "Outlet",
                                       "measurand": "Current.Import",
                                       "phase": "L1",
                                       "unit": "A",
                                       }],
                     "timestamp": "2022-07-26T19:23:13Z"}], connector_id=2, transaction_id=1234 )

           
          response= await self.call(request)

    async def stop_transaction(self):
          
          request=call.StopTransactionPayload( transaction_data=[{"sampledValue": [{"value": "000", "context": "Sample.Periodic",
                                       "format": "Raw",
                                       "location": "Outlet",
                                       "measurand": "Current.Import",
                                       "phase": "L1",
                                       "unit": "A",
                                       }],
                     "timestamp": "2022-07-26T19:23:13Z"}], meter_stop=1, timestamp=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z",  transaction_id=12, reason="SoftReset", id_tag="AA1234",  )


          response= await self.call(request)
    





async def main():
    
    

  try:

     async with websockets.connect(
              'ws://localhost:9000/CP_1',
             subprotocols=['ocpp1.6']
           ) as ws:
      

         cp = ChargePoint('CP_1', ws)
       
        

         task7=asyncio.ensure_future( cp.start())
         task1=asyncio.ensure_future( cp.send_heartbeat())
         task2=asyncio.ensure_future( cp.send_boot_notification())
         task3=asyncio.ensure_future( cp.authentication())
         task4=asyncio.ensure_future( cp.start_transaction())
         task5=asyncio.ensure_future( cp.send_meter_value())
         task6=asyncio.ensure_future( cp.stop_transaction())
       
       
         await asyncio.gather( task7, task1,  task2, task3, task4, task5, task6)




       
  except websockets.ConnectionClosed:  
      


      print(" -------Central System Closed-------------------- \n------------------ Connecting to the BACKUP SERVER-----------")  

      async with websockets.connect(
        'ws://localhost:8888/CP_1',
        subprotocols=['ocpp1.6']
    ) as websocket:

       

       cp = ChargePoint('CP_1', websocket)
       

       await asyncio.gather(cp.start(), cp.send_heartbeat(), 
       cp.send_boot_notification(),
       cp.authentication(), 
       cp.start_transaction(),  
       cp.stop_transaction(), 
       cp.send_meter_value(),
       cp.send_boot_notification(),
       cp.send_heartbeat())


      
      
    
   

if __name__ == "__main__":
   
   
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()


    
