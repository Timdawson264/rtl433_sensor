
//#define MSGPACK_DEBUGLOG_ENABLE
#include <MsgPack.h>
#include <RH_ASK.h>

struct beacon {
    MsgPack::str_t key_id {"id"};  uint16_t id;
    MsgPack::str_t key_temp {"t"}; float temp;
    MsgPack::str_t key_humi {"h"}; float humi;
    MSGPACK_DEFINE_MAP(key_temp, temp, key_humi, humi); // -> {"i":i, "f":f}
};
beacon mesurements;

RH_ASK driver(2000, 0, 10, 11, false);
MsgPack::Packer packer;


void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  driver.init();
  mesurements.id=123456789;
  mesurements.temp=987.65433;
  mesurements.humi=123.12345;
  
}

void loop() {
  mesurements.temp++;
  mesurements.humi++;
  packer.clear();
  packer.serialize(mesurements);   

  digitalWrite(LED_BUILTIN, HIGH); 
  driver.send(packer.data(), packer.size());
  driver.waitPacketSent();
  digitalWrite(LED_BUILTIN, LOW);
  delay(10000);      
}

