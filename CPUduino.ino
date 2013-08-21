#include <LiquidCrystal.h>

//Sample using LiquidCrystal library
/*******************************************************

This program will test the LCD panel and the buttons
Mark Bramwell, July 2010

********************************************************/

// select the pins used on the LCD panel
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

// define some values used by the panel and buttons
unsigned char lcd_key     = 0;
int adc_key_in  = 0;
#define DEBOUNCE   1
#define btnRIGHT  'r'
#define btnUP     'u'
#define btnDOWN   'd'
#define btnLEFT   'l'
#define btnSELECT 's'
#define btnNONE   'n'
#define btnENTER  'e'  //fake button

#define CPU_HELLO      'H'
#define CPU_STOP       'S'
#define CPU_OK         'O'
#define CPU_WRITE      'W'
#define CPU_WRITE_FULL 'F'
#define CPU_EXIT       'X'
#define ARD_BUTT       'B'
#define ARD_PASS       'P'

#define MAX_PASS 50
#define WMENU 16
#define HMENU 2
#define MENU_AREA WMENU * HMENU

#define UPARROW                 ((uint8_t)3)
#define DOWNARROW               ((uint8_t)4)
#define SELECT                  ((uint8_t)5)
#define HEART                   ((uint8_t)0)
#define SMILE                   ((uint8_t)2)
#define KEY                     ((uint8_t)1)

#define MENU1 0
#define MENU2   1
#define MENU3  2

#define BACKMAIN 0
#define SUBMENU1  1
#define SUBMENU2  2
#define SUBMENU3  3

#define MAINSUB 0
#define MAINLEN 2 //actual - 1
const char PROGMEM MenuStr1[] = "Linux Connect";
const char PROGMEM MenuStr2[] = "Wireless Conf";
const char PROGMEM MenuStr3[] = "Third menu";
#define XBEESUB 3 //starts at 2

#define XBEELEN 3  //actual - 1
const char PROGMEM Xbee1[] = "Back to Main";
const char PROGMEM Xbee2[] = "Linux Menu";
const char PROGMEM Xbee3[] = "SM1,ST3e8,SO1";
const char PROGMEM Xbee4[] = "WN,CN";

//currentmenu
#define MAIN   MAINSUB
#define XBEE   XBEESUB

PGM_P PROGMEM MenuTable[] = {
  MenuStr1,
  MenuStr2,
  MenuStr3,
  Xbee1,
  Xbee2,
  Xbee3,
  Xbee4
};

void lcd_puts_p(unsigned int ind)
{
  char buf[WMENU];
  PGM_P p;
  memcpy_P(&p, &MenuTable[ind], sizeof(PGM_P));
  strcpy_P(buf,p);

  lcd.print(buf);
}

inline const __FlashStringHelper * fromFlash(const char * pStr)
{
  return reinterpret_cast<const __FlashStringHelper *>(pStr);
}

byte Select[8]={  B01000,  B01100,  B00110,  B11111,  B11111,  B00110,  B01100,  B01000};

char menu = 0; //0 = main
char menulen = MAINLEN;
char menusel = 0;  //cursor
char index[20];
char currmenu = MAIN;  //current menu

// read the buttons
unsigned char read_LCD_buttons(char should_debounce,unsigned int time)
{
  unsigned char result;
  unsigned long starttime;
  while(1)
  {
  adc_key_in = analogRead(0);      // read the value from the sensor
  // my buttons when read are centered at these valies: 0, 144, 329, 504, 741
  // we add approx 50 to those values and check to see if we are close
  if (adc_key_in > 1000) continue; // We make this the 1st option for speed reasons since it will be the most likely result

  // For V1.1 us this threshold
  if (adc_key_in < 50)   result = btnRIGHT;
  else if (adc_key_in < 250)  result = btnUP;
  else if (adc_key_in < 450)  result = btnDOWN;
  else if (adc_key_in < 650)  result = btnLEFT;
  else if (adc_key_in < 850)  result = btnSELECT;
  else continue;

  if(should_debounce != DEBOUNCE && result != btnSELECT)
  {
    return result;
  }
  starttime = millis();
  //Debounce, wait for adc_key_in > 1000
  while(1)
  {
    //timeout for everything but select
    if(starttime + time < millis() && result != btnSELECT ) return result;
    adc_key_in = analogRead(0);
    if (adc_key_in > 1000) return result;
  }

  //return btnNONE;  // when all others fail, return this...
  }
}

//Utility that lets user enter a password, then prints that password to serial
//line
void enter_password()
{
  char buf[MAX_PASS];
  unsigned int buf_ind = 0;
  char lcd_x = 0;
  char lcd_y = 0;
  char button;
  unsigned char alpha_ind = 'a';
  unsigned char num_ind = 0;;
  unsigned char mode_ind = 0; //0 = lower, 1 = upper, 2 = number
  char select_ctr = 0;
  signed char inc = 0;
  lcd.clear();
  lcd.blink();

  //setup first character
  lcd_x = buf_ind % WMENU; //should give us which column to print to
  lcd_y = (buf_ind / WMENU) % HMENU; //should give us which row to print to
  lcd.write(alpha_ind);
  lcd.setCursor(lcd_x,lcd_y);

  memset(buf,0, sizeof(buf));
  //Loop to manage modes, enter text
  while(1)
  {
    inc = 0;
    button = read_LCD_buttons(DEBOUNCE,250);
    switch(button)
    {
      case btnRIGHT:
        if(select_ctr)
        {
          if(mode_ind == 0)
            buf[buf_ind++] = alpha_ind;
          else if(mode_ind == 1)
            buf[buf_ind++] = alpha_ind - 0x20;
          else
            buf[buf_ind++] = num_ind + 0x30;
          select_ctr = 0;
        }
        else
          inc = 1;
        break;
      case btnLEFT:
        if(select_ctr)
        {
          if(buf_ind > 0)
            buf_ind--;
          select_ctr = 0;
        }
        else
          inc = -1;
        break;
      case btnUP:
        if (mode_ind == 2)
          mode_ind = 0;
        else
          mode_ind++;
        break;
      case btnDOWN:
        if (mode_ind == 0)
          mode_ind = 2;
        else
          mode_ind--;
        break;
      case btnSELECT:
        if(select_ctr)
        {
          //select twice, we want to exit
          buf[buf_ind + 1] = '\n';
          buf[buf_ind + 2] = 0;
          Serial.print(buf);
          lcd.noBlink();
          return;
        }
        else
          select_ctr++;
        break;
    }
    if(button != btnSELECT)
    {
      if (mode_ind < 2)
      {
        if(inc == -1 && alpha_ind == 'a')
          alpha_ind = 'z';
        else if (inc == 1 && alpha_ind == 'z')
          alpha_ind = 'a';
        else
          alpha_ind += inc;
      }
      else
      {
        if(inc == -1 && num_ind == 0)
          num_ind = 9;
        else if (inc == 1 && num_ind == 9)
          num_ind = 0;
        else
          num_ind +=inc;
      }
      select_ctr = 0;
    }
    //now manipulate LCD
    lcd_x = buf_ind % WMENU; //should give us which column to print to
    lcd_y = (buf_ind / WMENU) % HMENU; //should give us which row to print to
    lcd.setCursor(lcd_x,lcd_y);

    if(mode_ind == 0)
      lcd.write(alpha_ind);
    else if(mode_ind == 1)
      lcd.write(alpha_ind - 0x20);
    else
      lcd.write(num_ind + 0x30);
    //put cursor back
    lcd.setCursor(lcd_x,lcd_y);

  }
}
//Function that dynamically displays on the character LCD, sending button
//presses via serial to the host
void linux_menu()
{
  char byte;
  char buf[WMENU + 1];
  unsigned int num;
  char button;
  char command_done = 0;
  int i;
  //announce that we are here
  sprintf(buf,"CPUduino,%d,%d",WMENU,HMENU);
  Serial.print(buf);

  while(1)
  {
    byte = Serial.read();

    if (byte == CPU_HELLO)
    {
      sprintf(buf,"CPUduino,%d,%d",WMENU,HMENU);
      Serial.print(buf);
    }
    else if (byte == CPU_OK)
    {
      //CPU confirmed
      byte = byte;
    }
    else if (byte == CPU_WRITE)
    {
      //CPU wants us to display the following strings
      lcd.clear();
      for(i = 0; i < HMENU; i++)
      {
        memset(buf, 0, sizeof(buf));
        num = Serial.readBytesUntil('\n',buf, sizeof(buf));
        buf[num] = 0;
        lcd.setCursor(1,i);
        lcd.print(buf);
      }
      byte = Serial.read();
      lcd.setCursor(0,byte);
      lcd.write(SELECT);

      command_done = 1;
    }
    else if (byte == CPU_WRITE_FULL)
    {
      //CPU wants us to display the following strings
      lcd.clear();
      for(i = 0; i < HMENU; i++)
      {
        memset(buf, 0, sizeof(buf));
        num = Serial.readBytesUntil('\n',buf, sizeof(buf));
        buf[num] = 0;
        lcd.setCursor(0,i);
        lcd.print(buf);
      }
      command_done = 1;
    }

    else if (byte == ARD_BUTT)
    {
      //CPU wants us to send the first button press
      button = read_LCD_buttons(DEBOUNCE,2000);
      Serial.write(button);
    }
    else if (byte == ARD_PASS)
    {
      //CPU wants us to get a password from the user
      enter_password();
      command_done = 1;
    }
    else if (byte == CPU_EXIT)
    {
      return;
    }
    if(command_done == 1)
    {
      Serial.print("OK\n");
      command_done=0;
    }
  }
}

void setup()
{
  Serial.begin(19200);
  lcd.begin(WMENU, HMENU);              // start the library

  lcd.createChar(5, Select);
  for(int i=0; i<20; i++)
    index[i] = i;

  lcd.clear();
}

//handle things here, not in loop
void select(uint8_t cmenu, uint8_t menus)
{
  switch(cmenu)
  {
    case MAIN:
      if(menus == MENU1)
      {
        menu=XBEESUB;
        menulen=XBEELEN;
        currmenu = XBEE;
      }
      else
        menu = MAINSUB;
      break;
    case XBEE:
      if(menus == BACKMAIN)
      {
        menu=MAINSUB;
        menulen=MAINLEN;
        currmenu = MAIN;
      }
      else if (menus == SUBMENU1)
      {
        //Linux connect
        linux_menu();
        menu = XBEESUB;
      }
      else
        menu = XBEESUB;
      break;
    default:
      break;
  }
  menusel = 0;
}



void loop()
{
  unsigned char button;

  lcd.clear();
  //simple menu here
  for(int i=0; i<HMENU && index[i+menu]-currmenu <= menulen ; i++)
  {
    lcd.setCursor(1,i);
    //lcd.print((__FlashStringHelper *)MenuTable[index[i+menu]]);
    lcd_puts_p(index[i+menu]);
    //lcd.print(fromFlash(MenuTable[index[i+menu]]));
  }

  //draw select
  lcd.setCursor(0,menusel);
  lcd.write(SELECT);
#ifdef DEBUG
  lcd.print((char)(menu + '0'));
  lcd.print(' ');
  lcd.print((char)(menusel + '0'));
#endif
  linux_menu();
  button = read_LCD_buttons(DEBOUNCE,3000);

  if(button == btnDOWN)
  {
    if(index[menu] - currmenu + HMENU-1  < menulen)  //space to potentially go down
      menu++;//increment menu
    else if(index[menusel + menu] - currmenu < menulen)
      menusel++;
    else
    {
      //at bottom of menu, go back to top
     menu = currmenu;
     menusel = 0;
    }
  }
  if(button == btnSELECT)
    select(currmenu, index[menusel+menu]-currmenu);

}
