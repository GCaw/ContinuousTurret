// NOTE: This program makes use of the micros() function to get the system time, the value overflows after approximately 70min, and as such the system should be reset once an hour if possible, if not possible code should be modified to make use of the millis() function which only overflows after 50 days.

long timenow;
double time1 = 0;
double time2 = 0;

int angle1 = 0; // value from serial factor of 800
int angle2 = 0; // value from serial factor of 800
int pos1 = 0; //stepper motor 1 counts, factor of 800
int pos2 = 0; //stepper motor 2 counts, factor of 800

int startup = 0;
long start;

byte inByte1 = 0; //first byte read on serial
byte inByte2 = 0; //second byte read on serial
byte inByte3 = 0; //third byte read on serial
byte move1 = 0; //set to true if one of the motors shoudl be moving
byte move2 = 0; //set to true if one of the motors shoudl be moving

int goto1 = -1; //position motor should go to, factor of 800
int goto2 = -1; //position motor should go to, factor of 800
int goat1 = 0; // speed that motor must travel at
int goat2 = 0; // speed motor must travle at
int angle1now = 0; // value from sensor, factor of 1024
int angle2now = 0; // value from sensor, factor of 1024

long timeprev1 = 0;
long timeprev2 = 0;
long prev = 0;

void setup()
{
  Serial.begin(19200);
  
  //PAN
  pinMode(13, OUTPUT);
  pinMode(2, OUTPUT); //motor clock
  pinMode(3, OUTPUT); //motor CW/CCW
  pinMode(4, OUTPUT); //sensor SELECT
  pinMode(5, OUTPUT); //sensor CLOCK
  pinMode(6, INPUT); //sensor DATA
  
  //TILT
  pinMode(8, OUTPUT); //motor clock
  pinMode(9, OUTPUT); //motor CW/CCW
  pinMode(10, OUTPUT);//sensor SELECT
  pinMode(11, OUTPUT);//sensor CLOCK
  pinMode(12, INPUT);//sensor DATA
  
  digitalWrite(2, HIGH);
  digitalWrite(3, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(5, HIGH);

    digitalWrite(13, HIGH);  
  digitalWrite(8, HIGH);
  digitalWrite(9, HIGH);
  digitalWrite(10, HIGH);
  digitalWrite(11, HIGH);

}


void loop()
{
  //read new commands
  if (Serial.available() > 0)
  {
     
    inByte1 = Serial.read();
    if (inByte1 > 127) //ie if the first bit is a 1
    {
       // digitalWrite(13, HIGH);
    	while (Serial.available() <= 0)
	{
	}
	inByte2 = Serial.read();
	
	while (Serial.available() <= 0)
	{
	}
        inByte3 = Serial.read();

        byte fhb1 = (inByte1 << 2);
        fhb1 = fhb1 >> 2;
        byte shb1 = (inByte2 >> 3);
        byte fhb2 = (inByte2 << 5);
        fhb2 = fhb2 >> 5;
        byte shb2 = inByte3;
        
	angle1 = (fhb1<<4) + shb1;
	angle2 = (fhb2<<7) + shb2;

	if ((inByte1 & B01000000) == B01000000)
	{
		position(angle1, angle2);
	}
	else
	{
		speed(angle1, angle2);
	}
    }

  }

  //read angle & send angle from sensor
  // 0 0 0 0 0 0 0 0 - 0 0 0 0 0 0 0 0
  //				   |- always 0
  //           |- Angle starts
  //       |- Used to indicate error 00, 01, 10, 11
  //   |- Used to indicate sensor 01, 10
  // |- Always 1
  
  
  if ((millis() - prev) > 50)
  {
    angle1now = readPosition(5, 6, 4);
    Serial.print ((angle1now >> 7)|B11100000, BYTE);
    byte tempang = angle1now;
    Serial.print (tempang & B01111111, BYTE);
    
    angle2now = readPosition(11, 12, 10);
    Serial.print ((angle2now >> 7)|B10100000, BYTE);
    tempang = angle2now;
    Serial.print (tempang & B01111111, BYTE);
    
    Serial.print ((pos1 >> 7)|B11000000, BYTE);
    tempang = pos1;
    Serial.print (tempang & B01111111, BYTE);
    
    Serial.print ((pos2 >> 7)|B10000000, BYTE);
    tempang = pos2;
    Serial.print (tempang & B01111111, BYTE);
    prev = millis();
    
  /*  if (startup && ((prev - start) > 5000))
    {
      double post1 = (angle1now/1024)*800;
      double post2 = (angle2now/1024)*800;
      pos1 = int(post1);
      pos2 = int(post2);
      startup = 0;
    }*/
  }

 //check if position/speed correct
	if (goto1 >= 0)
	{
		if (pos1 == angle1)
		{
			move1 = 0;
		}
	}
  	else
	{
		if (goat1 == 0)
		{
			move1 = 0;
		}
	}


	if (goto2 >= 0)
	{
		if (pos2 == angle2)
		{
			move2 = 0;
		}
	}
  	else
	{
		if (goat2 == 0)
		{
			move2 = 0;
		}
	}
	

  //step motors
    timenow = micros();
  if (((timenow - timeprev1 - (time1)) > 0) && move1)
  {
     if(digitalRead(8))
     {
        digitalWrite(8, LOW); 
        
          if (digitalRead(9))
        {
           pos1--;
           if (pos1 == -1)
             pos1 = 799;
        }
        else
        {
          pos1++;
           if (pos1 == 800)
             pos1 = 0;
             
        }
        timeprev1 = timenow;
     }
     else
        digitalWrite(8, HIGH);
  }
     
  if (((timenow - timeprev2 - (time2)) > 0) && move2)
  {
    if (digitalRead(2))
    {
      digitalWrite(2, LOW);
      
      if (digitalRead(3))
      {
         pos2--;
         if (pos2 == -1)
           pos2 = 799;
      }
      else
      {
        pos2++;
         if (pos2 == 801)
           pos2 = 1;
      }
      timeprev2 = timenow;
    }  
    else
      digitalWrite(2, HIGH);
  }
}


////////////////////////////////////////////
int readPosition(byte clock, byte data, byte select)
{
  unsigned int position = 0;

  //shift in our data  
  digitalWrite(select, LOW);
  delayMicroseconds(1);
  byte d1 = shiftIn(data, clock);
  byte d2 = shiftIn(data, clock);
  digitalWrite(select, HIGH);

  //get our position variable
  position = d1;
  position = position << 8;
//{| border="1"
//|-
//  position ||= d2;
//|}

position |= d2;

  position = position >> 6;

  //check the offset compensation flag: 1 == started up
  if (!(d2 & B00100000))
    position = 2048;//000 01 000 0 0000000

  //check the cordic overflow flag: 1 = error
  if (d2 & B00010000)
    position = 4096;//000 10 000 0 0000000

  //check the linearity alarm: 1 = error
  if (d2 & B00001000)
    position = 4096;//000 10 000 0 0000000

  //check the magnet range: 11 = error
  if ((d2 & B00000110) == B00000110)
    position = 6144;//000 11 000 0 0000000

  return position;
}

//read in a byte of data from the digital input of the board.
byte shiftIn(byte data_pin, byte clock_pin)
{
  byte data = 0;

  for (int i=7; i>=0; i--)
  {
    digitalWrite(clock_pin, LOW);
    delayMicroseconds(1);
    digitalWrite(clock_pin, HIGH);
    delayMicroseconds(1);

    byte bit = digitalRead(data_pin);
//{| border="1"
//|-
//    data ||= (bit << i);
    data |= (bit << i);
//|}

  }

 // Serial.print("byte: ");
 // Serial.println(data, BIN);

  return data;
}

void position (int ang1, int ang2)
{
	time1 = 11250;//equates to 40deg/s
	time2 = 11250;
	goto1 = ang1;
	goto2 = ang2;

        if (pos1 < ang1)
        {
            if ((ang1 - pos1) < abs(ang1 - 800 - pos1))
            {
              digitalWrite(9, LOW);
            }
            else
            {
              digitalWrite(9, HIGH);            
            }
        }
        else
        {
            if ((pos1-ang1) < abs(pos1 - ang1 - 800))
            {
               digitalWrite(9, HIGH);
            }
            else
            {
               digitalWrite(9, LOW);
            }
        }


        if (pos2 < ang2)
        {
            if ((ang2 - pos2) < abs(ang2 - 800 - pos2))
            {
              digitalWrite(3, LOW);
            }
            else
            {
              digitalWrite(3, HIGH);            
            }
        }
        else
        {
            if ((pos2-ang2) < abs(pos2 - ang2 - 800))
            {
               digitalWrite(3, HIGH);
            }
            else
            {
               digitalWrite(3, LOW);
            }
        }

	goat1 = 0;
	goat2 = 0;
        move1 = 1;
        move2 = 1;
}

void speed (int spd1, int spd2)//accept speed in deg/s
{
	goat1 = 1;
	goat2 = 1;
	goto1 = -1;
	goto2 = -1;
      
      if (spd1 > 0)
      {
          time1 = round(1000000/(spd1/0.45));
            move1 = 1;
      }
      else
      {
           move1 = 0;
      }
      if (spd2 > 0)
      {
        time2 = round(1000000/(spd2/0.45));
        move2 = 1;
      }
      else
      {
        move2 = 0;
      }
}
