#
#  telnet_server.py --- psedo telnet server (for practice of TeraTerm macro)
#
import sys
import socketserver
import datetime
import time

class MyTCPHandler(socketserver.BaseRequestHandler):
    login_status = False
    login_step = 0
    correct_id = 'user001'
    correct_pw = 'pass123'
    input_id = ''
    input_pw = ''
    prompt = '$ '
    
    def process_login(self, cmd_line):
      if self.login_step == 0:
        self.write('\r\nlogin:')
        self.login_step += 1
      elif self.login_step == 1:
        self.input_id = cmd_line
        if len(cmd_line) > 0:
          self.write('\r\npassword:')
          self.login_step += 1
        else:
          self.login_step = 0
      elif self.login_step == 2:
        self.input_pw = cmd_line
        print('input id=',self.input_id,' pw=',self.input_pw)
        if (self.input_id == self.correct_id) and (self.input_pw == self.correct_pw):
          self.write('\r\n===== Welcome to dummy telnet server!\r\n' + self.prompt)
          self.login_status = True
        else:
          self.write('\r\nlogin incorrect\r\n')
        self.login_step = 0 
      else:
        return

    def process_command(self, cmd_line):
      if (cmd_line == 'exit'):
          self.write('bye!\r\n\r\n')
          time.sleep(3)
          self.login_status = False
      elif (cmd_line == 'shutdown'):
          self.write('shutdown --- please exit!\r\n\r\n')
          time.sleep(5)
          sys.exit()
      elif (cmd_line == 'date'):
          self.write(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + "\r\n")
      elif (cmd_line == 'ls'):
          self.write('bin dev etc home  mnt   root  sys usr  var\r\n')
      elif (cmd_line == 'help'):
          cr = "\x0d\x0a"
          self.write('ls   : show list ' + cr)
          self.write('date : show current date,time ' + cr)
          self.write('exit : logout ' + cr)
          self.write('shutdown: shutdown server program ' + cr)
          self.write('help : show this help' + cr)
      else:
          #self.write('? unknown command\r\n')
          self.write('\r')

    def write(self, str):
        self.request.sendall(bytes(str,'UTF-8'))

    def handle(self):
        cmd_line = ''
        prompt = self.prompt
        
        self.request.sendall(b'\xff\xfb\x01')       # HOST WILL ECHO
        
        while True:
          self.data = self.request.recv(1024)
          a_byte = self.data
          for c in a_byte:
            a_charcode = c
            if a_charcode < 256:
              a_char = chr(a_charcode)

            if (a_charcode >= 0x20) and (a_charcode < 0x7f):
              cmd_line += a_char
              if self.login_step == 2:
                self.write('*')
              else:
                self.write(a_char)
            elif (a_charcode == 0x0d):        # CR
              if self.login_status:
                self.write("\r\n")
                print('cmd=',cmd_line)
                self.process_command(cmd_line)
                cmd_line = ''
                self.write(prompt)
              else:
                self.process_login(cmd_line)
              cmd_line = ''        
            elif  (a_charcode == 0x08):         # BS
              if len(cmd_line) > 0:
                self.write("\x08 \x08")
                cmd_line = cmd_line[:-1]
              else:
                self.write("\x07")  # BEL for notice
            elif (a_charcode == 0x03):         # Ctrl-C
              print('0x03')  #sys.exit()
            else:
              print('.') #print('(',c,')', sep="")

if __name__ == '__main__':
    print('telnet server start, waiting...')
    HOST, PORT = "localhost", 23
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
