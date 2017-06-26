#include <Sodaq_RN2483.h>

#define debugSerial SerialUSB
#define loraSerial Serial2

bool OTAA = true;

// ABP
// USE YOUR OWN KEYS!
const uint8_t devAddr[4] =
{
    0x00, 0x00, 0x00, 0x00
};

// USE YOUR OWN KEYS!
const uint8_t appSKey[16] =
{
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

// USE YOUR OWN KEYS!
const uint8_t nwkSKey[16] =
{
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

// OTAA
const uint8_t DevEUI[8] =
{
 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x89
};

const uint8_t AppEUI[8] =
{
  0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00

};

const uint8_t AppKey[16] =
{
  // 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00
  // 6e1eefa3b6bc4fadb9158bbd2bbf587c
  0x6e, 0x1e, 0xef, 0xa3, 0xb6, 0xbc, 0x4f, 0xad, 0xb9, 0x15, 0x8b, 0xbd, 0x2b, 0xbf, 0x58, 0x7c
};

void RED() {
 digitalWrite(LED_RED, LOW);
 digitalWrite(LED_GREEN, HIGH);
 digitalWrite(LED_BLUE, HIGH);
}
void GREEN() {
 digitalWrite(LED_RED, HIGH);
 digitalWrite(LED_GREEN, LOW);
 digitalWrite(LED_BLUE, HIGH);
}
void BLUE() {
 digitalWrite(LED_RED, HIGH);
 digitalWrite(LED_GREEN, HIGH);
 digitalWrite(LED_BLUE, LOW);
}
void LED_setup() {
 pinMode(LED_RED, OUTPUT);
 pinMode(LED_GREEN, OUTPUT);
 pinMode(LED_BLUE, OUTPUT);
}

void setup()
{
  while ((!debugSerial) && (millis() < 10000)){
    // Wait 10 seconds for debugSerial to open
  }
  
  debugSerial.begin(57600);
  loraSerial.begin(LoRaBee.getDefaultBaudRate());
  
  setupLoRa();

  LED_setup();

}

void setupLoRa(){
  if(!OTAA){
    // ABP
    setupLoRaABP();
  } else {
    //OTAA
    setupLoRaOTAA();
  }
}

void setupLoRaABP(){  
  if (LoRaBee.initABP(loraSerial, devAddr, appSKey, nwkSKey, false))
  {
    debugSerial.println("Communication to LoRaBEE successful.");
  }
  else
  {
    debugSerial.println("Communication to LoRaBEE failed!");
  }
}

void setupLoRaOTAA(){

  bool res = LoRaBee.initOTA(loraSerial, DevEUI, AppEUI, AppKey, false);
  debugSerial.println(res);
  
  if (res)
  {
    debugSerial.println("Network connection successful.");
  }
  else
  {
    debugSerial.println("Network connection failed!");
  }
}

void loop()
{
  BLUE();
  String reading = getTemperature();

    switch (LoRaBee.send(1, (uint8_t*)reading.c_str(), reading.length()))
    {
    case NoError:
      debugSerial.println("Successful transmission.");
      break;
    case NoResponse:
      debugSerial.println("There was no response from the device.");
      break;
    case Timeout:
      debugSerial.println("Connection timed-out. Check your serial connection to the device! Sleeping for 20sec.");
      delay(20000);
      break;
    case PayloadSizeError:
      debugSerial.println("The size of the payload is greater than allowed. Transmission failed!");
      break;
    case InternalError:
      debugSerial.println("Oh No! This shouldn't happen. Something is really wrong! The program will reset the RN module.");
      setupLoRa();
      break;
    case Busy:
      debugSerial.println("The device is busy. Sleeping for 10 extra seconds.");
      delay(10000);
      break;
    case NetworkFatalError:
      debugSerial.println("There is a non-recoverable error with the network connection. The program will reset the RN module.");
      setupLoRa();
      break;
    case NotConnected:
      debugSerial.println("The device is not connected to the network. The program will reset the RN module.");
      setupLoRa();
      break;
    case NoAcknowledgment:
      debugSerial.println("There was no acknowledgment sent back!");
      break;
    default:
      break;
    }

    const uint16_t receive_buffer_max_size = 128;
    uint8_t receive_buffer[receive_buffer_max_size];

    uint16_t receive_return_code = LoRaBee.receive(receive_buffer, 64);
    if (receive_return_code != 0)
    {
      for (int i = 0; i<receive_return_code; i++) {

        debugSerial.print("Received int: ");
        debugSerial.print(receive_buffer[i]);
        debugSerial.println(); 
        
        char buf[10];
        itoa (receive_buffer[i], buf, 10);
        debugSerial.print("Byte ");
        debugSerial.print(i);
        debugSerial.print(": ");
        debugSerial.print(buf);
        debugSerial.println();  
      }
      GREEN();
      debugSerial.println("Received some bytes..."); 
    } else {
      RED();
      debugSerial.println("Received nothing!"); 
    }
    /*
     * S-ORBA65630% curl -X POST --header 'Content-Type:application/json;charset=UTF-8' --header 'Accept: application/json' --header 'X-API-KEY: 6e1eefa3b6bc4fadb9158bbd2bbf587c' -d '{
  "data": "02",
  "port": 1,
  "confirmed": false
}' 'https://lpwa.liveobjects.orange-business.com/api/v0/vendors/lora/devices/0102030405060789/commands'
     */
     
    // Delay between readings
    // 60 000 = 1 minute
    delay(10000); 
}

String getTemperature()
{
  //10mV per C, 0C is 500mV
  float mVolts = (float)analogRead(TEMP_SENSOR) * 3300.0 / 1023.0;
  float temp = (mVolts - 500.0) / 10.0;
  
  return String(temp);
}
