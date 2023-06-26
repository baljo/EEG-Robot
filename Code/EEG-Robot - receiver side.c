/*
  Using EEG to control a Parallax ActivityBot through xBee
*/

#include "simpletools.h"
#include "ping.h"
#include "fdserial.h"
#include "abdrive.h"
#include "servo.h"

fdserial *xbee;
char response[25];
char ch;
const short int pingservo = 17;
volatile const short int pingsensor = 7;

void read_dist();  // Forward declaration
void init_xbee();
int *cog;           // For storing process ID
volatile int dist;  // Distance will be used by multiple cogs, hence volatile

int xbcmd(char *cmd, char *reply, int bytesMax, int msMax);


int main() {
  int x, y = 127;  //was y = 127
  int distHI, distLO;
  int tx_result, receiving;

  init_xbee();  // Initialises the XBee

  servo_angle(pingservo, 950);  // Initialising Ping-servo to XXX degrees
  pause(1000);


  cog = cog_run(&read_dist, 50);  // Run read_dist in other cog
  dist = ping_cm(pingsensor);


  while (1) {

    drive_setRampStep(5);  // 5 ticks/sec / 20 ms

    if (dist >= 255) {
      distHI = dist - 255;
      distLO = 255;
    } else {
      distHI = 0;
      distLO = dist;
    }

    // **** UNCOMMENT below row FOR TERMINAL DATA
    //    print("%c dist: %d  distHI: %d  distLO:  %d    %d    %d %c", HOME, dist, distHI, distLO, x, y, CLREOL);

    y = 127;
    int control = 99;
    int t_speed = 18;

    if (fdserial_rxReady) {
      control = fdserial_rxChar(xbee);
      y = fdserial_rxChar(xbee);  // receiving y (direction) from sender
    }

    if (control == 48 && y == 76)  // 48 = "0"
    {
      high(26);
      pause(50);
      low(26);
      y = 76;
      drive_rampStep(t_speed / 2, t_speed);
      //        print("Left\n");
    }

    if (control == 49 && y == 82)  // 49 = "1"
    {
      high(27);
      pause(50);
      low(27);
      y = 82;
      drive_rampStep(t_speed, t_speed / 2);
      //        print("Right\n");
    }

    if (control == 50 && y == 45)  // 45 = "-"
    {
      y = 45;
      drive_rampStep(t_speed, t_speed);
      //        print("Forward\n");
    }


    if (dist < 20)  // if too close, then reverse
      drive_speed(-t_speed, -t_speed);
  }

  cog_end(cog);
}


void read_dist() {
  while (1) {
    dist = ping_cm(pingsensor);
    pause(333);
  }
}


init_xbee() {
  // Initializing the XBee, some settings are router specific
  pause(1000);
  xbee = fdserial_open(9, 8, 0, 9600);
  pause(2000);
  print("\n\ncmd = +++\n");
  int bytes = xbcmd("+++", response, 10, 2000);
  if (bytes == 0)
    print("Timeout error.\n");
  else {
    print("reply = %s", response);

    print("cmd = ATID** YOUR SSID ** \n");
    xbcmd("ATID**YOUR_SSID**\r", response, 10, 200);
    print("reply = %s", response);

    print("cmd = ATAH2\n");
    xbcmd("ATAH2\r", response, 10, 200);
    print("reply = %s", response);

    print("cmd = ATMA1\n");
    xbcmd("ATMA1\r", response, 15, 200);
    print("reply = %s", response);

    print("cmd = ATAP0\n");
    xbcmd("ATAP0\r", response, 15, 200);
    print("reply = %s", response);

    print("cmd = ATEE2\n");
    xbcmd("ATEE2\r", response, 15, 200);
    print("reply = %s", response);

    print("cmd = ATPK**YOUR PASSWORD **\n");
    xbcmd("ATPK**YOUR_PASSWORD**\r", response, 20, 200);
    print("reply = %s", response);

    print("cmd = ATMY**SET YOUR IP**\n");
    xbcmd("ATMY**SET_YOUR_IP**\r", response, 15, 200);
    print("reply = %s", response);

    print("cmd = ATIP1\n");
    xbcmd("ATIP1\r", response, 10, 20);
    print("reply = %s", response);

    print("cmd = ATTMFFF\n");
    xbcmd("ATTMFFF\r", response, 10, 20);
    print("reply = %s", response);

    print("cmd = ATTSFfFF\n");
    xbcmd("ATTSFfFF\r", response, 10, 20);
    print("reply = %s", response);

    print("cmd = ATRO10\n");
    xbcmd("ATRO10\r", response, 10, 20);
    print("reply = %s", response);

    print("cmd = ATAI\n");
    xbcmd("ATAI\r", response, 10, 200);
    print("reply = %s", response);

    print("cmd = ATTP (temp)\n");
    xbcmd("ATTP\r", response, 10, 200);
    print("reply = %s", response);

    print("cmd = ATMY\n");
    xbcmd("ATMY\r", response, 15, 200);
    print("reply = %s\n", response);

    print("cmd = ATCN\n");
    xbcmd("ATCN\r", response, 10, 200);
    print("reply = %s", response);
  }
}


int xbcmd(char *cmd, char *reply, int bytesMax, int msMax) {
  int c = -1, n = 0;
  writeStr(xbee, cmd);
  memset(reply, 0, bytesMax);

  int tmax = (CLKFREQ / 1000) * msMax;
  int tmark = CNT;

  while (1) {
    c = fdserial_rxCheck(xbee);
    if (c != -1)
      reply[n++] = c;
    if (CNT - tmark > tmax)
      return 0;
    if (c == '\r')
      return n;
  }
}