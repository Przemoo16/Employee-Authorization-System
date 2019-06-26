#include <SoftwareSerial.h>
#include <MFRC522Extended.h>
#include <MFRC522.h>

#define RxD 2
#define TxD 3
#define SS_PIN 10
#define RST_PIN 9

SoftwareSerial BTSerial(RxD, TxD);
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

void setup() 
{
  BTSerial.flush();
  delay(500);
  BTSerial.begin(9600);
  
  Serial.begin(9600);   // Initiate a serial communication
  SPI.begin();      // Initiate  SPI bus
  mfrc522.PCD_Init();   // Initiate MFRC522
  Serial.println("Approximate your card to the reader...");
  Serial.println();

}
void loop() 
{
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  //Show UID on serial monitor
  Serial.print("UID tag :");
  String content= "";
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
     Serial.print(mfrc522.uid.uidByte[i], HEX);
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  Serial.println();
  Serial.print("Message : ");
  content.toUpperCase();
  if (content.substring(1) == "E0 CD 8F A3") //change here the UID of the card/cards that you want to give access
  {
    Serial.println("Authorized access");
    {
    BTSerial.write("Access;");
    }
    delay(1000);
  }
 
 else   {
    Serial.println(" Access denied");
    {
    BTSerial.write("Other;");
    }
    delay(1000);
  }
} 
