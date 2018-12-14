#!/usr/bin/python3


import sys

import threading

import time

from time import strftime

from time import sleep

import datetime

#####################
from tkinter import *
#####################

import signal , os

from PIL import Image, ImageTk

import schedule     ###   $pip3 install schedule

#################################

import gpiozero

from gpiozero import LED

import paho.mqtt.client as mqtt  # pip3 install paho-mqtt

import logging

import json


class Window(Frame):
      
      
      global cycle_timer , tick , tick1
      global state
     

      global run 

      global model_counter #, count1 , count2
      global no_plan , line_no

      no_plan=0      
      tick = 0
      tick1 = 0
      line_no=0
          
      def __init__(self,master):          
          super(Window,self).__init__(master)
                    
          global run 
          global client
          global mqtt_msg_arrival

          mqtt_msg_arrival = 0

                    
          self.master.rowconfigure(0, weight=1)
          self.master.columnconfigure(0, weight=1)
          self.grid(sticky=W+E+N+S)
          
          self.rowconfigure(0, weight=1)
          self.rowconfigure(1, weight=1)
          self.rowconfigure(2, weight=1)
          self.rowconfigure(3, weight=1)
          self.rowconfigure(4, weight=1)
          self.rowconfigure(5, weight=1)          
          self.rowconfigure(6, weight=1)
          self.rowconfigure(7, weight=1)
          self.rowconfigure(8, weight=1)
          self.rowconfigure(9, weight=1)          
          self.rowconfigure(10, weight=1)
          self.rowconfigure(11, weight=1)
          self.rowconfigure(12, weight=1)
          

          
          self.columnconfigure(0, weight=1)          
          self.columnconfigure(1, weight=1)
          self.columnconfigure(2, weight=1)          
          self.columnconfigure(3, weight=1) 
          self.columnconfigure(4, weight=1)          
          self.columnconfigure(5, weight=1)
          self.columnconfigure(6, weight=1)          
          self.columnconfigure(7, weight=1)
          self.columnconfigure(8, weight=1)
          self.columnconfigure(9, weight=1)
          self.columnconfigure(10, weight=1)          
          self.columnconfigure(11, weight=1)
          self.columnconfigure(12, weight=1)
          self.columnconfigure(13, weight=1)          
          self.columnconfigure(14, weight=1)


          
          print("run=",run)
          print(datetime.__file__)
          
          global relay
          relay = LED(5) #GPIO5
          relay.off

        
          #self.grid()
          #self.read_cfg_file()
          
          self.read_data_json()
          self.create_widgets()
          self.built_time_slot()

          
          #self.up_date_time_text()
          #mqtt_setup()
          

          ################# END MQTT #############################

          schedule.every().day.at("7:20").do(self.reset_all)

          schedule.every().day.at("7:19").do(self.logging_andon)

          schedule.every().day.at("20:00").do(self.reset_all)

          schedule.every().day.at("19:59").do(self.logging_andon)

          schedule.every().sunday.at("23:59").do(self.reboot)
          

          #schedule.every(5).seconds.do(self.time_slot_check)  

          #schedule.every().seconds.do(self.update_time)

          self.button_no_plan.config(text="___PLAN",fg="blue")          
              
          check_run = 1 #label run/hold show immediately after program run

      def mqtt_setup():
          
          ############### MQTT ############################

          MQTT_HOST = "192.168.0.101"
          MQTT_PORT = 1883
          MQTT_KEEPALIVE_INTERVAL = 60
          THIS_PI_IP ="192.168.0.103"

          logging.basicConfig(filename="history.log",level=logging.INFO)
          time1 = time.strftime("%H:%M:%S")
          date1 = time.strftime("%d/%m/%Y")
          logging.info("Program Started at " + date1 + "," + time1)

          

          #ip_address = str(check_output(['hostname','-I']))
          #print(ip_address)
          #ip_address.set(THIS_PI_IP)

          client = mqtt.Client()

          client.on_connect = self.on_connect
          client.on_disconnect = self.on_disconnect 
          client.on_message = self.on_message

          while True:
                try:
                     client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)          
                     print("[INFO]  : MQTT : MQTT Connect Complete")
                     break                 
                except:
                     print("ERROR Occurred")
                     break

          #client.loop_forever()
                    
          client.loop_start()
          
      def on_connect(self ,client ,userdata ,flags , rc):
            print("connected with result code "+str(rc))
            print("[INFO]  : MQTT : Connection returned result: " + mqtt.connack_string(rc))
            if(rc == 0):
               print("[INFO]  : MQTT : Connection Successful")
               client.subscribe("topic/test")   
               client.subscribe("topic/test1")
               client.subscribe("topic/date")
               logging.info("[INFO]  : MQTT : Connection Successful")     
            else:
               print("rc=" + rc)
               


      def on_disconnect(self, client, userdata, rc):
          if rc != 0:
              print(" Unexpected disconnection")
              
          """    
          while(True):
             try:
                 print("Trying to Reconnect")
                 client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
                 break
             except:
                 print("Error in Retrying to Connect with Broker")
                 continue
          """
          
      def on_message(self ,client, userdata, msg):
            
            global run , mqtt_msg_arrival

            global plan , actual , bal 
            
            print("message received ->" + msg.topic + " " + str(msg.payload)) #print received message
            
            msg_payload_str = str(msg.payload , 'utf-8')
            print("msg_payload_str=", msg_payload_str)
            
            if msg.topic == "topic/date" :
                  
                        mqtt_msg_arrival = 1


                        self.save_data()
                        
                        time.sleep(1)
                        
                        print("set system time")
                        #subprocess.call(shlex.split("sudo date -s '09 May 2018 19:17:17'"))
                        subprocess.call(shlex.split("sudo date -s" + " " + "'" + msg_payload_str + "'"))
                        subprocess.call(shlex.split("sudo hwclock -w"))

                        print ("auorestart")
                        python = sys.executable
                        os.execl(python ,python , * sys.argv)
 

                        
                        #time.sleep(1)
                        #os.execv('/home/pi/assy_lineb_plant1_slave.py',[''])
                        #os.execv(sys.executable,[sys.executable] + ['assy_lineb_plant1_slave.py'])
                        
                      
                        mqtt_msg_arrival = 0
                 
      
            """
            time1 = time.strftime("%H:%M:%S")
            date1 = time.strftime("%d/%m/%Y")
            
            if msg.payload.decode() == "Relay-Off":
                  print("Relay-Off")
                  self.label_relay_status.configure(text = "Relay-Off" ,fg = "red")
                  logging.info("relay Off at "+ date1 + "," + time1 )     

            if msg.payload.decode() == "Relay-On":
                  print("Relay-On")
                  self.label_relay_status.configure(text = "Relay-On" ,fg = "white")
                  logging.info("relay On at "+ date1 + "," + time1 )  
               
            """      

      def send_relay_on(self):
          try:
                 client.publish("topic/test","Relay-On", 1, False)  # QoS =1 Retain = False
          except Exception as e:
                 print(str(e))


      def restart(self):  #RESTART WILL FUNCTION  ON THE SHELL (TERMIT) /NOT IN IDLE
            
            print ("auorestart")
            python = sys.executable
            os.execl(python ,python , * sys.argv)


      def is_time_in_range(self,start,end,x):
            #true if x is in range
            if start <= end:
                  return start <= x <= end
            else:
                  return start <= x or x <= end #understand this part
            


      def update_time(self):  #secondly running
          
          
                    
          #time1 = time.strftime("%H:%M:%S")
          #date1 = date.strftime("%d/%m/%Y")
          now=datetime.datetime.now()
          time1 = now.strftime("%H:%M:%S")
          date1 = now.strftime("%d/%m/%Y")
          
          self.label_time.configure(text = time1)
          self.label_date.configure(text = date1)

          
          


      def run_hold_status(self):
            global run
            run = not run
            if run :          
               self.label_run.config(text="RUN",fg="blue")
               #tick1 = 0 #running CT reset

            if not run:      
               self.label_run.config(text="HOLD",fg="red")

            print("run=",run)

      def no_plan_status(self):
            global run
            global no_plan #no_plan=1 (no production) / no_plan=0 (production on progress)

            no_plan = not no_plan
            if no_plan :
              
               self.button_no_plan.config(text="NO PLAN",fg="red")
               
            if not no_plan:
               
               self.button_no_plan.config(text="___PLAN ",fg="blue")


            
          
      def run_status(self):
             global run , tick1
             run = True             
             self.label_run.config(text="RUN",fg="blue")
             #tick1 = 0 #running CT reset

             
      def hold_status(self):
             global run
             run= False       
             self.label_run.config(text="HOLD",fg="red")    


      def plan_up(self): #secondly running
            
          global cycle_timer , run1 , run , plan , tick1 , plan

          if run:
                tick1 += 1
                self.label_running_second.configure(text = str(tick1)) 
                if tick1 >= cycle_timer:
                      plan = plan_int.get()          
                      plan += 1                       
                      plan_int.set(plan)
                      tick1 = 0 #running CT reset
         

      def signal_handler(signal,frame):
            exit(0)
           
          
      def reset_all(self):    
          #target_int.set(1234)
          global plan , actual , parts_losstime , qc_losstime , mc_losstime
          
          plan=0
          actual=0
          bal=0
          plan_int.set(plan)
          actual_int.set(actual)
          bal_int.set(0)
          achievement.set(0)
          
          parts_losstime_float.set(0)
          qc_losstime_float.set(0)
          mc_losstime_float.set(0)
          
          parts_losstime = 0
          qc_losstime = 0
          mc_losstime = 0

          self.save_data_json() 

          
      def quit_program(self):
          print("quit")
          root.destroy()
          
      def shutdown(self):
          print("now shutdown")
          check_call(['sudo', 'poweroff'])



      def reboot(self):          
                command = "/usr/bin/sudo /sbin/shutdown -r now"
                import subprocess
                process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                output = process.communicate()[0]
                print (output)
                
      def plan_count(self):
                global cycle_timer , tick , tick1 , run1 , run , no_plan
                global check_run , plan , actual , bal

  
                if run:
                   if not no_plan:
                      tick1 = tick1 + 1
                      #temp = "{0:.1f}".format(tick1)
                      #self.label_running_second.configure(text = str(temp))
                      self.label_running_second.configure(text = str(tick1)) 
                      if tick1 >= cycle_timer:
                            plan = plan_int.get()          
                            plan += 1                       
                            plan_int.set(plan)
                            tick1 = 0 #running CT reset
                            bal = actual - plan
                            bal_int.set(bal)
                            if plan != 0:
                               percent = actual/plan * 100
                            else:
                               percent = 0
                            temp = "{0:.1f}".format(percent)
                            percent =  temp
                            achievement.set(str(percent))  
                            self.save_data_json()              


                    
      def up_date_time_text(self):
          
             global cycle_timer , tick , tick1 , run
             global check_run , plan , actual , bal
             global mqtt_msg_arrival

         
             while True:

                if check_run == 1:   #label run/hold show immediately after program run        
                      if run == True :    
                              self.label_run.config(text="RUN",fg="blue")
                              check_run = 0 
                      if run == False:
                              self.label_run.config(text="HOLD",fg="red")
                              check_run = 0

                tick += 1
                if tick > 5:  # 1 sec
                   #self.update_time()
                   #self.time_slot_check()
                   self.plan_count()
                   self.update_time()
                   tick=0
               
                """
                if run1==True: #RUN SWITCH ON
                   run=True
                else:
                   run=False
                """
                '''
                if run:
                   if not no_plan:
                      tick1 = tick1 + 0.1
                      temp = "{0:.1f}".format(tick1)
                      self.label_running_second.configure(text = str(temp)) 
                      if tick1 >= cycle_timer:
                            plan = plan_int.get()          
                            plan += 1                       
                            plan_int.set(plan)
                            tick1 = 0 #running CT reset
                            bal = actual - plan
                            bal_int.set(bal)
                            if plan != 0:
                               percent = actual/plan * 100
                            else:
                               percent = 0
                            temp = "{0:.1f}".format(percent)
                            percent =  temp
                            achievement.set(str(percent))  
                            self.save_data_json()              
                '''
                schedule.run_pending()
                time.sleep(0.2)
                #root.after(100,self.up_date_time_text) #100 ms period / 0.1 sec
          
      def ct_change(self):
          global cycle_timer, tick , tick1 
          global ct_str
                    
          tick=0
          tick1=0
          print("ct change")
          ct_str = self.entry_ct.get()        
          cycle_timer = float(ct_str)  #sec         
          print("ct:",ct_str,"cycle timer:",cycle_timer)
          
      def get_sec(self,time_str):
            h , m , s = time_str.split(':')
            return int(h)*3600 + int(m)*60 + int(s)

      def checktime(self,ix):
            if(int(ix) < 10):
                  ix = "0" + ix
            return ix



      def built_time_slot(self):
            
            global a  , b  , c ,  d ,  e ,  f,   g , h ,  i ,  j  , k ,  l
            global a1 , b1 , c1 , d1 , e1 , f1 , g1, h1 , i1 , j1 , k1 , l1
            global a2 , b2 , c2 , d2 , e2 , f2 , g2, h2 , i2 , j2 , k2 , l2

            #SHIFT 1 SENIN - KAMIS
            a = "07:20:00"
            b = "09:30:00"

            c = "09:40:00"
            d = "12:00:00"

            e = "12:45:00"
            f = "14:30:00"            

            g = "14:40:00"
            h = "16:00:00"

            i = "16:15:00"
            j = "18:15:00"

            k = "18:30:00"
            l = "19:00:00"
            #SHIFT 1 JUMAT
            a1 = "07:20:00"
            b1 = "09:30:00"

            c1 = "09:40:00"
            d1 = "11:45:00"

            e1 = "13:00:00"
            f1 = "14:30:00"            

            g1 = "14:40:00"
            h1 = "16:30:00"

            i1 = "16:45:00"
            j1 = "18:15:00"

            k1 = "18:30:00"
            l1 = "19:00:00"            
            #SHIFT 2
            a2 = "20:00:00"
            b2 = "22:00:00"

            c2 = "22:10:00"
            d2 = "23:59:59"

            e2 = "00:30:00"
            f2 = "02:30:00"            

            g2 = "02:40:00"
            h2 = "04:00:00"

            i2 = "04:15:00"
            j2 = "06:00:00"

            k2 = "00:00:00"
            l2 = "00:00:00"
            #shift 1
            a = self.get_sec(a)
            b = self. get_sec(b)

            c = self.get_sec(c)
            d = self.get_sec(d)

            e = self.get_sec(e)
            f = self.get_sec(f)


            g = self.get_sec(g)
            h = self.get_sec(h)


            i = self.get_sec(i)
            j = self.get_sec(j)
             
            k = self.get_sec(k)
            l = self.get_sec(l)
            

                        
            #jumat
            a1 = self.get_sec(a1)
            b1 = self.get_sec(b1)

            c1 = self.get_sec(c1)
            d1 = self.get_sec(d1)

            e1 = self. get_sec(e1)
            f1 = self.get_sec(f1)


            g1 = self.get_sec(g1)
            h1 = self.get_sec(h1)


            i1 = self.get_sec(i2)
            j1 = self.get_sec(j2)


            k1 = self.get_sec(k1)
            l1 = self.get_sec(l1)
            
            #shift 2
            a2 = self.get_sec(a2)
            b2 = self.get_sec(b2)

            c2 = self.get_sec(c2)
            d2 = self.get_sec(d2)

            e2 = self.get_sec(e2)
            f2 = self.get_sec(f2)


            g2 = self.get_sec(g2)
            h2 = self.get_sec(h2)


            i2 = self.get_sec(i2)
            j2 = self.get_sec(j2)


            k2 = self.get_sec(k2)
            l2 = self.get_sec(l2)
                        


      #TIME SLOT CHECK (RUN STATUS)
      def time_slot_check(self):

            global a  , b  , c ,  d ,  e ,  f,   g , h ,  i ,  j  , k ,  l
            global a1 , b1 , c1 , d1 , e1 , f1 , g1, h1 , i1 , j1 , k1 , l1
            global a2 , b2 , c2 , d2 , e2 , f2 , g2, h2 , i2 , j2 , k2 , l2
                              
            global run          
            global check_run , run_old
            global plan , actual , bal
            global parts_losstime , qc_losstime ,mc_losstime 


            while True:
                
                #print("time slot")
                day_nos = datetime.datetime.today().weekday()  #weekday : monday=0,tuesday=1,wednesday=2,thursday=3,friday=4,sat=5,sunday=6          
                now = strftime("%H:%M:%S")
                print("day_no=",day_nos," time :",now)               
                now = self.get_sec(now)

                shift1 = "07:20:00"  #RESET AWAL SHIFT1
                shift1 = self.get_sec(shift1)

                #reset shift1
                if now == shift1:
                    plan = 0
                    actual = 0
                    bal = 0
                    plan_int.set(plan)
                    actual_int.set(actual)
                    bal_int.set(bal)
                    achievement.set(0)

                    parts_losstime = 0
                    qc_losstime = 0
                    mc_losstime = 0
                    
                    parts_losstime_float.set(parts_losstime)
                    qc_losstime_float.set(qc_losstime) 
                    mc_losstime_float.set(mc_losstime)

                    self.save_data_json()

                shift2 = "20:00:00"  #RESET AWAL SHIFT2
                shift2 = self.get_sec(shift2)
                #reset shift2
                if now == shift2:
                    plan = 0
                    actual = 0
                    bal = 0
                    plan_int.set(plan)
                    actual_int.set(actual)
                    bal_int.set(bal)
                    achievement.set(0)
                    
                    parts_losstime = 0
                    qc_losstime = 0
                    mc_losstime = 0
                    
                    parts_losstime_float.set(parts_losstime)
                    qc_losstime_float.set(qc_losstime) 
                    mc_losstime_float.set(mc_losstime)                    
                    self.save_data_json()
                    
                
          
                if (now > shift1) and (now < a2) and (day_nos != 4): #SHIFT1 NON JUMAT
                                  
                                  
                          if a <= now and now <= b:
                                   run = True
                                   print("run=",run , "slot a-b")
                                        
                          elif c <= now and now <= d:     
                                   run = True
                                   print("run=",run , "slot c-d")
                                        
                          elif e <= now and now <= f: 
                                   run = True
                                   print("run=",run , "slot e-f")  
                             
                          elif g <= now and now <= h:     
                                   run = True
                                   print("run=",run , "slot g-h")
                                        
                          elif i <= now and now <= j: 
                                   run = True
                                   print("run=",run , "slot e-f") 
                             
                          elif k <= now and now <= l:     
                                   run = True
                                   print("run=",run , "slot k-l") 
                                              
                          else:
                                   run = False
                                   print("shift1 non jumat not in between")
                                   #self.label_run.config(text="HOLD",fg="red")
                                  
                          if run :
                                   self.label_run.config(text="RUN",fg="green")
                          else:                  
                                   self.label_run.config(text="HOLD",fg="red") 
  
                if (now > shift1) and (now < a2) and (day_nos == 4) : #SHIFT 1 & JUMAT
                                  
                                  
                          if a1 <= now and now <= b1:
                                   run = True
                                   print("run=",run , "slot a1-b1")
                                        
                          elif c1 <= now and now <= d1:     
                                   run = True
                                   print("run=",run , "slot c1-d1")
                                        
                          elif e1 <= now and now <= f1: 
                                   run = True
                                   print("run=",run , "slot e1-f1")  
                             
                          elif g1 <= now and now <= h1:     
                                   run = True
                                   print("run=",run , "slot g1-h1")
                                        
                          elif i1 <= now and now <= j1: 
                                   run = True
                                   print("run=",run , "slot e1-f1") 
                             
                          elif k1 <= now and now <= l1:     
                                   run = True
                                   print("run=",run , "slot k1-l1") 
                                              
                          else:
                                   run = False
                                   print("shift1 jumat not in between")
                                   #self.label_run.config(text="HOLD",fg="red")
                          if run :
                                   self.label_run.config(text="RUN",fg="green")
                          else:
                                   self.label_run.config(text="HOLD",fg="red")
                                   
                if (now > shift2)  or  (now < shift1) :   #SHIFT2
                                  
                                  
                          if a2<= now and now <= b2:
                                   run = True
                                   print("run=",run , "slot a2-b2")
                                        
                          elif c2 <= now and now <= d2:     
                                   run = True
                                   print("run=",run , "slot c2-d2")
                                        
                          elif e2 <= now and now <= f2: 
                                   run = True
                                   print("run=",run , "slot e2-f2")  
                             
                          elif g2 <= now and now <= h2:     
                                   run = True
                                   print("run=",run , "slot g2-h2")
                                        
                          elif i2 <= now and now <= j2: 
                                   run = True
                                   print("run=",run , "slot e2-f2") 
                             
                          elif k2 <= now and now <= l2:     
                                   run = True
                                   print("run=",run , "slot k2-l2") 
                                              
                          else:
                                   run = False
                                   print("shift2 not in between")
                                   #self.label_run.config(text="HOLD",fg="red")
                          if run :
                                   self.label_run.config(text="RUN",fg="green")
                          else:
                                   self.label_run.config(text="HOLD",fg="red") 
                              
                time.sleep(5)
                   
      def select_model(self):
          global model_counter
          global cycle_timer
          

          model_counter += 1
          if model_counter > 5 :
                model_counter = 1

          if model_counter == 1 :
                var11.set(part_name1)
                var12.set(ct1)
                var14.set(ct1)
                
                ct_str = ct1
                cycle_timer = float(ct_str)   #in sec

          if model_counter == 2 :
                var11.set(part_name2)
                var12.set(ct2)
                var14.set(ct2)
                
                ct_str = ct2
                cycle_timer = float(ct_str)   #in sec
                
          if model_counter == 3 :
                var11.set(part_name3)
                var12.set(ct3)
                var14.set(ct3)
                
                ct_str = ct3
                cycle_timer = float(ct_str)   #in sec


          if model_counter == 4 :
                var11.set(part_name4)
                var12.set(ct4)
                var14.set(ct4)
                
                ct_str = ct4
                cycle_timer = float(ct_str)   #in sec


          if model_counter == 5 :
                var11.set(part_name5)
                var12.set(ct5)
                var14.set(ct5)
                
                ct_str = ct5
                cycle_timer = float(ct_str)   #in sec
                          

      def logging_andon(self):
          global plan , actual , parts_losstime , qc_losstime , mc_losstime , line_no
          
          print ("logging ...")
          
          line_no +=1
          
          filename = "/media/usb/log_data.txt"

          if os.path.exists(filename):
             append_write = 'a' # append if already exists
          else:
             line_no = 1  
             append_write = 'w' # make a new file if not
             log_file = open(filename,append_write)
             #log_file.write("date   " + "model   " + "parts L/T   " + "qc L/T " + "mc L/T  "   + '\n')
             log_file.write("{} , {} , {} , {} , {} , {}    \n".format("NO.","NAME","date","PARTS L/T(min)","QC L/T(min)" ,"MC L/T(min)"  ))
             append_write = 'a'
             log_file.close()
            
          log_file = open(filename,append_write)
          
          field1 = str(line_no)
          field2 = self.entry_part_name.get()
          field3 = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y   ")
          field4 = str(parts_losstime)
          field5 = str(qc_losstime)
          field6 = str(mc_losstime)
          log_file.write("{} , {} , {} , {} , {}, {}\n".format(field1 ,field2,field3 ,field4 , field5, field6)) 
          log_file.close()
  
      def dummy_data_json(self):
                
          data_json = {
                
          "line_name" : "ASSY LINE" ,       
          "plan": 0 ,                    
          "actual" : 0  ,         
          "model_counter" : 1 ,
          "part_name1" : "part_name1" ,
          "part_name2" : "part_name2" ,             
          "part_name3" : "part_name3" ,
          "part_name4" : "part_name4" ,
          "part_name5" : "part_name5" ,
          "ct1" : 1 ,
          "ct2" : 2 ,
          "ct3" : 3 ,
          "ct4" : 4 ,
          "ct5" : 5 ,
          "parts_losstime" : 0 ,
          "qc_losstime" : 0 ,
          "mc_losstime" : 0 ,
          
          }

          with open('/media/usb/time_f.json','w') as json_file:
                print(data_json)
                json.dump(data_json , json_file , indent=4 )

                
      def save_data_json(self):

          global part_name1 , part_name2 , part_name3 , part_name4 , part_name5 ,  line_name    
          global ct1 , ct2 , ct3 , ct4 , ct5            
          global plan , actual 
          global model_counter
          global cycle_timer            
          global parts_losstime , qc_losstime , mc_losstime
          
          print("saving data as json")        
          self.ct_change()
           
          if model_counter == 1 :
                part_name1  = self.entry_part_name.get()
                ct1 = self.entry_ct.get()
                
          if model_counter == 2 :
                part_name2 = self.entry_part_name.get()
                ct2 = self.entry_ct.get()
               
                
          if model_counter == 3 :
                part_name3 = self.entry_part_name.get()
                ct3 = self.entry_ct.get()
            
          if model_counter == 4 :
                part_name4 = self.entry_part_name.get()
                ct4 = self.entry_ct.get()

          if model_counter == 5 :
                part_name5 = self.entry_part_name.get()
                ct5 = self.entry_ct.get()
                         
          #built json data
          data_json = {
                
          "line_name" : self.entry_line.get()  ,       
          "plan": int(self.entry_plan.get()) ,                    
          "actual" : int(self.entry_actual.get())  ,         
          "model_counter" : model_counter ,
          "part_name1" : part_name1 ,
          "part_name2" : part_name2 ,             
          "part_name3" : part_name3 ,
          "part_name4" : part_name4 ,
          "part_name5" : part_name5 ,
          "ct1" : ct1 ,
          "ct2" : ct2 ,
          "ct3" : ct3 ,
          "ct4" : ct4 ,
          "ct5" : ct5 ,

          "parts_losstime" : parts_losstime ,
          "qc_losstime" : qc_losstime ,
          "mc_losstime" : mc_losstime ,
          }
          
          with open('/media/usb/time_f.json','w') as json_file:
                print(data_json)
                json.dump( data_json  , json_file , indent=4 )



      # Open the file for reading.
      def read_data_json(self):
            
          global part_name1 , part_name2 , part_name3 , part_name4 , part_name5 , line_name    
          global ct1 , ct2 , ct3 , ct4 , ct5
          global plan , actual ,  bal , cycle_timer , ct_str
          global model_counter     
          global achievement
          global parts_losstime , qc_losstime , mc_losstime
          
          try:
                with open('/media/usb/time_f.json') as json_file:
                         data_json = json.load(json_file)
                         print(data_json)
          except:
                self.dummy_data_json() #use default if not exist/error
                #re-read data
                with open('/media/usb/time_f.json') as json_file:
                         data_json = json.load(json_file)

          line_name = data_json["line_name"]
          
          plan = int(data_json["plan"])
          plan_int.set(plan)
          
          actual = int(data_json["actual"]) 
          actual_int.set(actual)

          bal = actual - plan
          bal_int.set(bal)

          if plan != 0:
             percent = actual/plan * 100
          else:
             percent = 0
          temp = "{0:.1f}".format(percent)
          percent =  temp
          achievement.set(str(percent))            
      
          model_counter = int(data_json["model_counter"])
          
          part_name1 = data_json["part_name1"]
          part_name2 = data_json["part_name2"]
          part_name3 = data_json["part_name3"]
          part_name4 = data_json["part_name4"]
          part_name5 = data_json["part_name5"]
          
          ct1 = data_json["ct1"]
          ct2 = data_json["ct2"]          
          ct3 = data_json["ct3"]
          ct4 = data_json["ct4"] 
          ct5 = data_json["ct5"]

          parts_losstime = float(data_json["parts_losstime"])
          qc_losstime = float(data_json["qc_losstime"]) 
          mc_losstime = float(data_json["mc_losstime"])

          parts_losstime_float.set(parts_losstime)
          qc_losstime_float.set(qc_losstime) 
          mc_losstime_float.set(mc_losstime)         
          

          var1.set(part_name1)  #PART NO NAME 1(P/N)
          var2.set(part_name2)  #PART NO NAME 2(P/N)
          var3.set(part_name3)  #PART NO NAME 3(P/N)
          var4.set(part_name4)  #PART NO NAME 4(P/N) 
          var5.set(part_name5)  #PART NO NAME 5(P/N)

          var6.set(ct1)   #CT 1
          var7.set(ct2)   #CT 2
          var8.set(ct3)   #CT 3
          var9.set(ct4)   #CT 4         
          var10.set(ct5)  #CT 5        
          
          var13.set(line_name)  #LINE NAME : ASSEMBLY G
          
          if model_counter == 1 :
                var11.set(part_name1)
                var12.set(ct1)
                var14.set(ct1)
                
                ct_str = ct1
                cycle_timer = float(ct_str)   #in sec

          if model_counter == 2 :
                var11.set(part_name2)
                var12.set(ct2)
                var14.set(ct2)
                
                ct_str = ct2
                cycle_timer = float(ct_str)   #in sec
                
          if model_counter == 3 :
                var11.set(part_name3)
                var12.set(ct3)
                var14.set(ct3)
                
                ct_str = ct3
                cycle_timer = float(ct_str)   #in sec

          if model_counter == 4 :
                var11.set(part_name4)
                var12.set(ct4)
                var14.set(ct4)
                
                ct_str = ct4
                cycle_timer = float(ct_str)   #in sec

          if model_counter == 5 :
                var11.set(part_name5)
                var12.set(ct5)
                var14.set(ct5)
                
                ct_str = ct5
                cycle_timer = float(ct_str)   #in sec
                           
          
      def create_widgets(self):   

          #ENTRY "line name" 
          self.entry_line = Entry(self ,
              bg='RoyalBlue1', #color of background
              #bitmap = from file
              bd = 1 , #border size
              #cursor
              font = "Arial 70 bold", #color of font
              #font = "7-Segment 70 bold", #color of font
              fg = "white" , #color of text
              #relief=SUNKEN,width=10) ,
              justify = CENTER, #left/right/center
              textvariable = var13,
              relief= RIDGE ,width=8)
     
         
          #ENTRY "line name" 
          self.entry_part_name = Entry(self ,
              bg='RoyalBlue1', #color of background
              #bitmap = from file
              bd = 1 , #border size
              #cursor
              font = "Arial 50 bold", #color of font
              #font = "7-Segment 70 bold", #color of font
              fg = "white" , #color of text
              #relief=SUNKEN,width=10) ,
              justify = CENTER, #left/right/center
              textvariable = var11,
              relief= RIDGE ,width=8)

          
          #LOGO
          self.label_logo = Label(self, 
                            compound = CENTER,
                            text="",
                            relief=SUNKEN ,                    
                            image=logo ,
                            width=5)
         
          
          #RUN/HOLD 
          self.label_run = Label(self,
              anchor = CENTER ,
              bg = 'gold' , #color of background
              #bitmap = from file
              bd = 1 , #border size
              #cursor
              font = "Times 60 bold", #color of font
              fg = "red" , #color of text
              height = 1 , #vertical dimension of the new frame
              #image = to display a static image in label widget
              justify =  LEFT , #left/right/center
              padx = 0 , #extra space added to the left and right of the text
              #within widget , default=1
              pady = 0 , #extra space added above and below of the text
              relief=SUNKEN,
              text='',
              width=4)          

          #DATE 
          self.label_date = Label(self,
              anchor = CENTER ,
              bg = 'green' , #color of background
              #bitmap = from file
              bd = 1 , #border size
              #cursor
              font = "Times 30 bold", #color of font
              fg = "white" , #color of text
              height = 1 , #vertical dimension of the new frame
              #image = to display a static image in label widget
              justify =  "left" , #left/right/center
              padx = 0 , #extra space added to the left and right of the text
              #within widget , default=1
              pady = 0 , #extra space added above and below of the text      
              relief=FLAT ,
              text = "" ,
              width=3)
          
          #logo date
          self.label_text_date= Label(self,
               anchor = CENTER ,
               bg = 'green' , #color of background
               #bitmap = from file
               bd = 1 , #border size
               #cursor
               font = "Times 30 bold", #color of font
               fg = "blue" , #color of text
               height = 1 , #vertical dimension of the new frame
               #image = to display a static image in label widget
               justify =  "left" , #left/right/center
               padx = 0 , #extra space added to the left and right of the text
               #within widget , default=1
               pady = 0 , #extra space added above and below of the text
               #within widget , default=1
               #relief = , #specify the appearance of border            
               relief=RIDGE,
               text='DATE',
               width=3)

          #TIME
          self.label_time = Label(self,
              anchor = CENTER ,
              bg = 'green' , #color of background
              #bitmap = from file
              bd = 5 , #border size
              #cursor
              font = "Times 30 bold", #color of font
              fg = "white" , #color of text
              height = 1 , #vertical dimension of the new frame
              #image = to display a static image in label widget
              justify =  "left" , #left/right/center
              padx = 2 , #extra space added to the left and right of the text
              relief=FLAT,
              text = "" ,
              width=3)
              
          #text time
          self.label_text_time= Label(self,
               anchor = CENTER ,
               bg = 'green' , #color of background
               #bitmap = from file
               bd = 1 , #border size
               #cursor
               font = "Times 30 bold", #color of font
               fg = "blue" , #color of text
               height = 1 , #vertical dimension of the new frame
               #image = to display a static image in label widget
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text
               #within widget , default=1
               pady = 1 , #extra space added above and below of the text      
               relief=RIDGE,
               text='TIME',
               width=3)

          #CYCLE TIME
          self.label_cycle_time = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Times 25 bold", #color of font
               fg = "white" , #color of text
               height = 1 , #vertical dimension of the new frame
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text 
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='TAKT TIME',
               width=3)
          
          #ENTRY CYCLE TIME
          self.entry_ct = Entry(self ,
               bg='yellow', #color of background
               bd = 1 , #border size
               font = "Times 25 bold", #color of font
               fg = "black" , #color of text
               justify =  "center" , #left/right/center
               textvariable = var14 ,
               relief=FLAT,width=3)

          #LABEL RUNNING CYCLE TIME
          self.label_running_second = Label(self,
               anchor = CENTER ,
               bg = 'magenta' , #color of background
               bd = 1 , #border size
               font = "Times 25 bold", #color of font
               fg = "white" , #color of text
               height = 1 , #vertical dimension of the new frame
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text
               pady = 1 , #extra space added above and below of the text           
               relief=RIDGE,
               text='SEC',
               width=3)               

          #TEXT SECOND
          self.label_text_second = Label(self,
               anchor = CENTER ,
               bg = 'blue' , #color of background
               bd = 1 , #border size
               font = "Times 25 bold", #color of font
               fg = "white" , #color of text
               height = 1 , #vertical dimension of the new frame
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text
               pady = 1 , #extra space added above and below of the text          
               relief=RIDGE,
               text='SEC',
               width=3)

          #PRD PLAN
          self.label_plan = Label(self,
              anchor = CENTER ,
              bg = 'black' , #color of background
              #bitmap = from file
              bd = 1 , #border size
              #cursor
              font = "Piboto 100 bold", #color of font
              fg = "white" , #color of text
              height = 1 , #vertical dimension of the new frame
              #image = to display a static image in label widget
              justify =  "left" , #left/right/center
              padx = 0 , #extra space added to the left and right of the text
              #within widget , default=1
              pady = 0, #extra space added above and below of the text
              relief=RIDGE,
              text='PLAN',
              width=4)
          

          #ENTRY "PRODUCTION PLAN" 
          self.entry_plan = Entry(self ,
              bg='white', #color of background
              #bitmap = from file
              bd = 1 , #border size
              #cursor
              font = "DSEG7Classic 100 bold", #color of font
              #font = "7-Segment 70 bold", #color of font
              fg = "red" , #color of text
              #relief=SUNKEN,width=10) ,
              justify = CENTER, #left/right/center
              textvariable = plan_int ,
              relief= SUNKEN ,width=4)

          
          #LOT TARGET
          self.label_plan_lot = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               #bitmap = from file
               bd = 1 , #border size
               #cursor
               font = "Times 100 bold", #color of font
               fg = "yellow" , #color of text
               height = 1 , #vertical dimension of the new frame
               #image = to display a static image in label widget
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text
               #within widget , default=1
               pady = 1 , #extra space added above and below of the text
               #within widget , default=1
               #relief = , #specify the appearance of border            
               relief=RIDGE,
               text='Pcs',
               width=4)

          #ACTUAL
          self.label_actual = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               #bitmap = from file
               bd = 1 , #border size
               #cursor
               font = "Piboto 100 bold", #color of font
               fg = "white" , #color of text
               height = 1 , #vertical dimension of the new frame
               #image = to display a static image in label widget
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text
               #within widget , default=1
               pady = 1 , #extra space added above and below of the text
               #within widget , default=1
               #relief = , #specify the appearance of border      
               relief=RIDGE,
               text='ACTUAL',
               width=4)

          #ENTRY  ACTUAL  
          self.entry_actual = Entry(self ,
              bg='white', #color of background
              #bitmap = from file
              bd = 1 , #border size
              #cursor
              font = "DSEG7Classic 100 bold", #color of font
              fg = "red" , #color of text
              justify =  "center" , #left/right/center
              #relief=SUNKEN,width=10)
                                     
              textvariable = actual_int,
              relief=SUNKEN,width=4)
          

          #LOT
          self.label_actual_lot = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               #bitmap = from file
               bd = 1 , #border size
               #cursor
               font = "Times 100 bold", #color of font
               fg = "yellow" , #color of text
               height = 1 , #vertical dimension of the new frame
               #image = to display a static image in label widget
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text
               #within widget , default=1
               pady = 1 , #extra space added above and below of the text
               #within widget , default=1
               #relief = , #specify the appearance of border      
               relief=RIDGE,
               text='Pcs',
               width=4)


          #BALANCE
          self.label_balance = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Piboto 90 bold", #color of font
               fg = "white" , #color of text
               height = 1 , #vertical dimension of the new frame  
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text   
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='BALANCE',
               width=4)

          #ENTRY  BALANCE 
          self.entry_balance = Entry(self ,
              bg='white', #color of background
              bd = 1 , #border size
              font = "DSEG7Classic 100 bold", #color of font
              fg = "red" , #color of text
              justify =  "center" , #left/right/center                                    
              textvariable = bal_int,
              relief=SUNKEN,width=4)
          
          #LOT
          self.label_balance_lot = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Times 100 bold", #color of font
               fg = "yellow" , #color of text
               height = 1 , #vertical dimension of the new frame
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='Pcs',
               width=4)

          #ACHIEVEMENT
          self.label_achievement = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Piboto 90 bold", #color of font
               fg = "white" , #color of text
               height = 1 , #vertical dimension of the new frame  
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text   
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='ACHIEV',
               width=4)

          #ENTRY ACHIEVEMENT
          self.entry_achievement = Entry(self ,
              bg='white', #color of background
              bd = 1 , #border size
              font = "DSEG7Classic 100 bold", #color of font
              fg = "red" , #color of text
              justify =  "center" , #left/right/center                                    
              textvariable = achievement ,
              relief=SUNKEN,width=4)
          
          #ACHIEVEMTN %
          self.label_achievement_percent = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Times 100 bold", #color of font
               fg = "yellow" , #color of text
               height = 1 , #vertical dimension of the new frame
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='%',
               width=4)


          #LOSS TIME parts
          self.label_parts_losstime = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Piboto 30 bold", #color of font
               fg = "green" , #color of text
               height = 1 , #vertical dimension of the new frame  
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text   
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='L/T PARTS(minutes)',
               width=4)

          #ENTRY L/T parts
          self.entry_parts_losstime = Entry(self ,
              bg='black', #color of background
              bd = 1 , #border size
              font = "DSEG7Classic 30 bold", #color of font
              fg = "green" , #color of text
              justify =  "center" , #left/right/center                                    
              textvariable = parts_losstime_float ,
              relief=SUNKEN,width=4)

          self.label_sec_parts = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Piboto 30 bold", #color of font
               fg = "green" , #color of text
               height = 1 , #vertical dimension of the new frame  
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text   
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='MIN',
               width=4)
          
          #LOSS TIME qc
          self.label_qc_losstime = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Piboto 30 bold", #color of font
               fg = "yellow" , #color of text
               height = 1 , #vertical dimension of the new frame  
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text   
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='L/T QC(minutes)',
               width=4)

          #ENTRY L/T parts
          self.entry_qc_losstime = Entry(self ,
              bg='black', #color of background
              bd = 1 , #border size
              font = "DSEG7Classic 30 bold", #color of font
              fg = "yellow" , #color of text
              justify =  "center" , #left/right/center                                    
              textvariable = qc_losstime_float,
              relief=SUNKEN,width=4)
          
          self.label_sec_qc = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Piboto 30 bold", #color of font
               fg = "yellow" , #color of text
               height = 1 , #vertical dimension of the new frame  
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text   
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='MIN',
               width=4)


          #LOSS TIME equipmnet
          self.label_mc_losstime = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Piboto 30 bold", #color of font
               fg = "red" , #color of text
               height = 1 , #vertical dimension of the new frame  
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text   
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='L/T MTE (minutes)',
               width=4)

          #ENTRY L/T parts
          self.entry_mc_losstime = Entry(self ,
              bg='black', #color of background
              bd = 1 , #border size
              font = "DSEG7Classic 30 bold", #color of font
              fg = "red" , #color of text
              justify =  "center" , #left/right/center                                    
              textvariable = mc_losstime_float ,
              relief=SUNKEN,width=4)

          self.label_sec_mc = Label(self,
               anchor = CENTER ,
               bg = 'black' , #color of background
               bd = 1 , #border size
               font = "Piboto 30 bold", #color of font
               fg = "red" , #color of text
               height = 1 , #vertical dimension of the new frame  
               justify =  "left" , #left/right/center
               padx = 1 , #extra space added to the left and right of the text   
               pady = 1 , #extra space added above and below of the text
               relief=RIDGE,
               text='MIN',
               width=4)
          
                    
          #BUTTON SAVE DATA
          self.write_data = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                command = self.save_data_json ,
                font = "Times 10 bold" ,
                height = 1 ,
                text = 'save')

          #BUTTON LOG DATA
          self.log_data = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                command = self.logging_andon ,
                font = "Times 10 bold" ,
                height = 1 ,
                text = 'log data')

          #BUTTON fullscreen change
          self.fullscreen_change = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                #command = self.quit_program ,
                command =toggle_fullscreen ,                          
                 font = "Times 10 bold" ,
                height = 1 ,
                justify="left" ,
                text = 'Zoom/Exit')

          #BUTTON RUN HOLD
          self.button_run_hold = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                command = self.run_hold_status ,
                font = "Times 10 bold" ,
                height = 1 ,
                text = 'RUN/HOLD')
          
         #BUTTON RESET ALL
          self.button_reset_all = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                command = self.reset_all ,
                font = "Times 10 bold" ,
                height = 1 ,
                text = 'RESET')
          
         #BUTTON RESTART
          self.button_restart = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                command = self.restart ,
                font = "Times 10 bold" ,
                height = 1 ,
                text = 'RESTART')

         #BUTTON REBOOT
          self.button_reboot = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                command = self.reboot ,
                font = "Times 10 bold" ,
                height = 1 ,
                text = 'REBOOT')

          
         #BUTTON SELECT MODEL
          self.button_select_model = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                command = self.select_model ,
                font = "Times 10 bold" ,
                height = 1 ,
                text = 'SELECT') 

        #BUTTON NO PLAN
          self.button_no_plan = Button(self,
                bg = 'green' ,
                anchor = CENTER ,
                #bitmap
                bd = 1 ,
                command = self.no_plan_status ,
                font = "Times 20 bold" ,
                height = 1 ,
                text = 'NO PLAN')    
          
          #sticky=E+W+S+N
          self.label_logo.grid(sticky=E+W+S+N,row=0,column=0,rowspan=2,columnspan=4)

          self.entry_line.grid(sticky=E+W+S+N,row=0,column=4,rowspan=1,columnspan=8)

          self.entry_part_name.grid(sticky=E+W+S+N,row=1,column=4,columnspan=8)
          
          self.label_run.grid(sticky=E+W+S+N,row=0,column=12,rowspan=2,columnspan=4)
          
          
          self.label_text_date.grid(sticky=E+W+S+N,row=2,column=0,columnspan=4)
          
          self.label_date.grid(sticky=E+W+S+N,row=2,column=4,columnspan=4)

          self.label_text_time.grid(sticky=E+W+S+N,row=2,column=8,columnspan=4)
          
          self.label_time.grid(sticky=E+W+S+N,row=2,column=12,columnspan=4)


          
          #BUTTON COMMAND WIDGET
          self.fullscreen_change.grid(row=2,column=3,sticky=NE)          
          self.write_data.grid(row=2,column=11,sticky=NE)
          self.log_data.grid(row=0,column=4,sticky=NW)
          #self.button_opr1.grid(row=8,column=3,sticky=NE)
          self.button_reset_all.grid(row=2,column=14,sticky=NE)
          self.button_run_hold.grid(row=0,column=14,sticky=NE)
          self.button_no_plan.grid(row=0,column=12,sticky=NW)  
          self.button_restart.grid(row=2,column=0,sticky=NW)
          self.button_reboot.grid(row=0,column=0,sticky=NW)
          self.button_select_model.grid(row=1,column=4,sticky=NW)
 
          self.label_cycle_time.grid(sticky=E+W+S+N,row=3,column=0,columnspan=4)
          self.entry_ct.grid(sticky=E+W+S+N,row=3,column=4,columnspan=4)          
          self.label_running_second.grid(sticky=E+W+S+N,row=3,column=8,columnspan=4)        
          self.label_text_second.grid(sticky=E+W+S+N,row=3,column=12,columnspan=4)
          
          self.label_plan.grid(sticky=E+W+S+N,row=4,column=0,rowspan=3,columnspan=6)          
          self.entry_plan.grid(sticky=E+W+S+N,row=4,column=6,rowspan=3,columnspan=6)          
          self.label_plan_lot.grid(sticky=E+W+S+N,row=4,column=12,rowspan=3,columnspan=4)
                                   
          self.label_actual.grid(sticky=E+W+S+N,row=7,column=0,rowspan=3,columnspan=6)         
          self.entry_actual.grid(sticky=E+W+S+N,row=7,column=6,rowspan=3,columnspan=6)
          self.label_actual_lot.grid(sticky=E+W+S+N,row=7,column=12,rowspan=3,columnspan=4)
                    
          self.label_balance.grid(sticky=E+W+S+N,row=10,column=0,rowspan=3,columnspan=6)          
          self.entry_balance.grid(sticky=E+W+S+N,row=10,column=6,rowspan=3,columnspan=6)
          self.label_balance_lot.grid(sticky=E+W+S+N,row=10,column=12,rowspan=3,columnspan=4)

          self.label_achievement.grid(sticky=E+W+S+N,row=13,column=0,rowspan=3,columnspan=6)          
          self.entry_achievement.grid(sticky=E+W+S+N,row=13,column=6,rowspan=3,columnspan=6)
          self.label_achievement_percent.grid(sticky=E+W+S+N,row=13,column=12,rowspan=3,columnspan=4)          
          
          self.label_parts_losstime.grid(sticky=E+W+S+N,row=16,column=0,rowspan=1,columnspan=5)
          self.entry_parts_losstime.grid(sticky=E+W+S+N,row=17,column=0,rowspan=2,columnspan=5)
          
          #self.label_sec_parts.grid(sticky=E+W+S+N,row=16,column=12,rowspan=1,columnspan=4)

          self.label_qc_losstime.grid(sticky=E+W+S+N,row=16,column=5,rowspan=1,columnspan=6)
          self.entry_qc_losstime.grid(sticky=E+W+S+N,row=17,column=5,rowspan=2,columnspan=6)
          
          #self.label_sec_qc.grid(sticky=E+W+S+N,row=17,column=12,rowspan=1,columnspan=4)

          self.label_mc_losstime.grid(sticky=E+W+S+N,row=16,column=11,rowspan=1,columnspan=5)
          self.entry_mc_losstime.grid(sticky=E+W+S+N,row=17,column=11,rowspan=2,columnspan=5)
          
          #self.label_sec_mc.grid(sticky=E+W+S+N,row=18,column=12,rowspan=1,columnspan=4)
          
          
def shutdown():
    print("now shutdown")
    check_call(['sudo', 'poweroff'])


def parts_losstime_bt_when_pressed():
    global start_time_float1
    
    start_time_float1 = time.time()  #TIMER 1 START
    
def parts_losstime_bt_when_released(): 
    global parts_losstime
    global start_time_float1
    
    finish_time_float1 = time.time()  #TIMER 1 STOP
        
    parts_losstime = finish_time_float1 -  start_time_float1
    parts_losstime = parts_losstime / 60
    
    temp = float(parts_losstime_float.get())
    parts_losstime = parts_losstime + temp
    parts_losstime = float("{0:.2f}".format(parts_losstime))
    
    parts_losstime_float.set(parts_losstime)
    app.save_data_json               

def qc_losstime_bt_when_pressed():
    global start_time_float2
    
    start_time_float2 = time.time()  #TIMER 2 START
    
def qc_losstime_bt_when_released(): 
    global qc_losstime
    global start_time_float2
    
    finish_time_float2 = time.time()  #TIMER 2 STOP
        
    qc_losstime = finish_time_float2 -  start_time_float2
    qc_losstime = qc_losstime / 60
    
    temp = float(qc_losstime_float.get())
    qc_losstime = qc_losstime + temp
    qc_losstime = float("{0:.2f}".format(qc_losstime))
    
    qc_losstime_float.set(qc_losstime)
    app.save_data_json


def mc_losstime_bt_when_pressed():
    global start_time_float3
    
    start_time_float3 = time.time()  #TIMER 3 START
    
def mc_losstime_bt_when_released(): 
    global mc_losstime
    global start_time_float3
    
    finish_time_float3 = time.time()  #TIMER 3 STOP
        
    mc_losstime = finish_time_float3 -  start_time_float3
    mc_losstime = mc_losstime / 60
    
    temp = float(mc_losstime_float.get())
    mc_losstime = mc_losstime + temp
    mc_losstime = float("{0:.2f}".format(mc_losstime))
    
    mc_losstime_float.set(mc_losstime)
    app.save_data_json



def actual_trigger():
        global plan , actual , bal
        #print("triger")
        actual_int.set(actual_int.get() + 1)
        print (actual_int.get())
        plan = plan_int.get()
        actual = actual_int.get()
        bal = actual - plan
        bal_int.set(bal)
        if plan != 0:
           percent = actual/plan * 100
        else:
           percent = 0
        temp = "{0:.1f}".format(percent)
        percent =  temp
        achievement.set(str(percent))                
        app.save_data_json

        
def buzzer_trigger():
      global relay_count
      relay_count += 1
      if relay_count == 1:         
         relay.on()
      else:
            relay.off()
            relay_count = 0

def center_form():
    # Apparently a common hack to get the window size. Temporarily hide the
    # window to avoid update_idletasks() drawing the window in the wrong
    # position.
    root.withdraw()
    root.update_idletasks()  # Update "requested size" from geometry manager

    xx = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    yy = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.geometry("+%d+%d" % (xx, yy))

    # This seems to draw the window frame immediately, so only call deiconify()
    # after setting correct window position
    root.deiconify()


def toggle_fullscreen():
    global state
    """
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('+%d+%d' % (x, y)) ## this part allows you to only change the location
    """
    
    
    state = not state  # Just toggling the boolean
    if state:
         center_form 
         root.attributes("-fullscreen", True)
         root.attributes('-zoomed', False)
         
    else:
         center_form 
         root.attributes('-zoomed', True)
         root.attributes("-fullscreen", False)
    #print("press")
    return



if __name__ == '__main__':
                                 
      root = Tk()

      plan_int = IntVar()
      actual_int = IntVar()                             
      bal_int = IntVar()
      achievement = StringVar()
      
      parts_losstime_float = StringVar()
      qc_losstime_float = StringVar()
      mc_losstime_float = StringVar()

      ct_str = StringVar() #real number
                             
      var1 = StringVar()  #MODEL 1 NAME
      var2 = StringVar()  #MODEL 2 NAME
      var3 = StringVar()  #MODEL 3 NAME
      var4 = StringVar()  #MODEL 4 NAME
      var5 = StringVar()  #MODEL 5 NAME

      var6 = StringVar()  #MODEL 1 CT
      var7 = StringVar()  #MODEL 2 CT
      var8 = StringVar()  #MODEL 3 CT
      var9 = StringVar()  #MODEL 4 CT
      var10 = StringVar() #MODEL 5 CT 

      var11 = StringVar() #current p/n
      var12 = StringVar() #current c/t

      var13 = StringVar() #LINE NAME  EX : "ASSEMBLY G"

      var14 = StringVar() #CT default

      puasa = StringVar()  #"puasa"
    

      #GLOBAL VAR
      #target_int = IntVar()
                             
      run = False
      state = True
      check_run = 1  #start up HOLD/RUN label
      relay_count = 0
  
      #trigger output
      count = 0
      prev_inp = 1
      #run/hold switch
      count1 = 0
      prev_inp1 = 0
      run1 = False

      scroll_text = False


      #################### LOGO ##############################

      pil_image = Image.open("/media/usb/tbina_logo.jpg")  
      width_org,height_org = pil_image.size         
      factor=0.3
      width = int(width_org*factor)
      height = int(height_org*factor)
      pil_image2 = pil_image.resize((width,height),Image.ANTIALIAS)
      image2  = ImageTk.PhotoImage(pil_image2)

      logo = image2 
                                                                  
      root.title("COUNTER DISPLAY")
      #root.geometry("1360x768+0+0")
      #root.geometry("1280x720+0+0")
      root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
      root.attributes("-fullscreen", True)
      #root.attributes('-zoomed', True)

      center_form
                        
      app=Window(root)
      app.configure(bg = 'cyan')

      #signal.signal(signal.SIGINT,signal_handler)
      #signal.pause
      #GPIO.cleanup()
      
     
      t1 = threading.Thread(name='time_slot' , target= app.time_slot_check)
      t1.start()
          
      t2 = threading.Thread(name='update_time_plan' , target= app.up_date_time_text)
      t2.start()      
      
      
      '''
      while True:
            app.time_slot_check
            time.sleep(5)
      while True:
            app.up_date_time_text
            time.sleep(1)
      '''
      actual_btn = gpiozero.Button(17 , hold_time=0.1)
      actual_btn.when_held = actual_trigger

      parts_btn = gpiozero.Button(27 , hold_time=0.1)
      
      parts_btn.when_pressed = parts_losstime_bt_when_pressed
      parts_btn.when_released = parts_losstime_bt_when_released

      qc_btn = gpiozero.Button(22 , hold_time=0.1)

      qc_btn.when_pressed = qc_losstime_bt_when_pressed
      qc_btn.when_released = qc_losstime_bt_when_released

      mc_btn = gpiozero.Button(10 , hold_time=0.1)
      
      mc_btn.when_pressed = mc_losstime_bt_when_pressed
      mc_btn.when_released = mc_losstime_bt_when_released

      #buzzer_btn = gpiozero.Button(27 , hold_time=0.1)
      #buzzer_btn.when_held = buzzer_trigger 
      
      
      #shutdown_btn = gpiozero.Button(22 , hold_time=2)
      #shutdown_btn.when_held = shutdown

      root.mainloop()

      

#####################################################################################################





      
"""
PUASA

time table jam kerja FTR PLANT 1 :

1.SHIFT 1   SENIN SD KAMIS    : 07.00 - 16.00
            ISTIRAHAT         : 10.00 - 10.10
                              : 12.00 - 13.00
                              : 14.30 - 14.40   
                             
                              
            JUMAT             : 07.00 - 16.00
            ISTIRAHAT         : 10.00 - 10.10
                              : 11.30 - 12.45
                              : 14.30 - 14.40
                              
    OVER TIME (SENIN SD JUMAT): 16.10 - 18.00
                              

1.SHIFT 2   SENIN SD JUMAT    : 20.00 - 05.00
            ISTIRAHAT         : 22.00 - 22.10
                              : 00.00 - 00.30
                              : 02.00 - 02.10   
            ISTIRAHAT/SAHUR   : 03.30 - 04.00

    OVER TIME (SENIN SD JUMAT): 05.10 - 07.00                
                              

##############################################            
NON PUASA

time table jam kerja FTR PLANT 1 :

1.SHIFT 1   SENIN SD KAMIS    : 08.00 - 17.00
            ISTIRAHAT         : 10.00 - 10.10
                              : 12.00 - 13.00
                              : 14.30 - 14.40   
                             
                              
            JUMAT             : 08.00 - 17.00
            ISTIRAHAT         : 10.00 - 10.10
                              : 11.30 - 13.00
                              : 14.30 - 14.40
                              
    OVER TIME (SENIN SD JUMAT): 17.10 - 20.00
                              

1.SHIFT 2   SENIN SD JUMAT    : 20.00 - 05.00
            ISTIRAHAT         : 22.00 - 22.10
                              : 00.00 - 01.00
                              : 03.00 - 03.10   
                     
    OVER TIME (SENIN SD JUMAT): 05.10 - 08.00

            
"""

'''
          if puasa.get() == "puasa":
                Puasa = True
                print("WE ARE in ramadhan") 
          else:
                Puasa = False
                print("WE ARE not in ramadhan") 
                  
          
          #DETERMINE RUN/HOLD STATUS WHEN PROGRAM START
          #datetime.datetime.today().weekday()
          #Monday=0 , sunday=6

          #for testing only
          """
          start = datetime.time(20,0,0)
          end = datetime.time(22,0,0)
          now=datetime.datetime.now()
          now_time=now.time()
          print("test",self.is_time_in_range(start,end,now_time))
          print("today weekday number",datetime.datetime.today().weekday())
          """
          
          #WORK TIME
          #MONDAY/TUESDAY/WEDNESDAY/THURSDAY (run status)
          day_nos = datetime.datetime.today().weekday()
          now=datetime.datetime.now()
          now_time=now.time()
          print("today weekday number=",datetime.datetime.today().weekday())
          
          if (day_nos == 0) or (day_nos == 1) or (day_nos == 2) or (day_nos == 3) or (day_nos == 5) or(day_nos == 6)  :
             if not Puasa:
                #shift1
                start1 = datetime.time(10,0,0)  #hold
                end1 = datetime.time(10,10,0)                                
                hold1 = self.is_time_in_range(start1,end1,now_time)

                start2 = datetime.time(12,0,0) #hold
                end2 = datetime.time(13,0,0)
                hold2 = self.is_time_in_range(start2,end2,now_time)

                start3 = datetime.time(14,30,0)  #hold
                end3 = datetime.time(14,40,0)
                hold3 = self.is_time_in_range(start3,end3,now_time)

                #shift 2
                start4 = datetime.time(22,0,0)  #hold
                end4 = datetime.time(22,10,0)
                hold4 = self.is_time_in_range(start4,end4,now_time)

                start5 = datetime.time(0,0,0)  #hold
                end5 = datetime.time(1,0,0)
                hold5 = self.is_time_in_range(start5,end5,now_time)

                start6 = datetime.time(3,0,0)  #hold
                end6 = datetime.time(3,10,0)
                hold6 = self.is_time_in_range(start6,end6,now_time)                
                
          
                if hold1 or hold2 or hold3 or hold4 or hold5 or hold6  :
                      run = False
                      self.hold_status()
                else:
                      run = True
                      self.run_status()
                
                print("start up run=",hold1,hold2,hold3,hold4,hold5,hold6)

             if Puasa:
                #shift1
                start1 = datetime.time(10,0,0)  #hold
                end1 = datetime.time(10,10,0)                                
                hold1 = self.is_time_in_range(start1,end1,now_time)

                start2 = datetime.time(12,0,0) #hold
                end2 = datetime.time(13,0,0)
                hold2 = self.is_time_in_range(start2,end2,now_time)

                start3 = datetime.time(14,30,0)  #hold
                end3 = datetime.time(14,40,0)
                hold3 = self.is_time_in_range(start3,end3,now_time)

                #shift 2
                start4 = datetime.time(22,0,0)  #hold
                end4 = datetime.time(22,10,0)
                hold4 = self.is_time_in_range(start4,end4,now_time)

                start5 = datetime.time(0,0,0)  #hold
                end5 = datetime.time(0,30,0)
                hold5 = self.is_time_in_range(start5,end5,now_time)

                start6 = datetime.time(2,0,0)  #hold
                end6 = datetime.time(2,10,0)
                hold6 = self.is_time_in_range(start6,end6,now_time)

                start7 = datetime.time(3,30,0)  #hold
                end7 = datetime.time(4,0,0)
                hold7 = self.is_time_in_range(start7,end7,now_time)               
                
          
                if hold1 or hold2 or hold3 or hold4 or hold5 or hold6 or hold7 :
                      run = False
                      self.hold_status()
                else:
                      run = True
                      self.run_status()
                
                print("start up run=",hold1,hold2,hold3,hold4,hold5,hold6)


          if (day_nos == 4): #or (day_nos == 6) :  #HARI JUMAT
             if not Puasa:    
                start1 = datetime.time(10,0,0)  #hold
                end1 = datetime.time(10,10,0)                                
                hold1 = self.is_time_in_range(start1,end1,now_time)

                start2 = datetime.time(11,30,0) #hold
                end2 = datetime.time(13,0,0)
                hold2 = self.is_time_in_range(start2,end2,now_time)

                start3 = datetime.time(14,30,0)  #hold
                end3 = datetime.time(14,40,0)
                hold3 = self.is_time_in_range(start3,end3,now_time)

                
                #shift 2
                start4 = datetime.time(22,0,0)  #hold
                end4 = datetime.time(22,10,0)
                hold4 = self.is_time_in_range(start4,end4,now_time)

                start5 = datetime.time(0,0,0)  #hold
                end5 = datetime.time(1,0,0)
                hold5 = self.is_time_in_range(start5,end5,now_time)

                start6 = datetime.time(3,0,0)  #hold
                end6 = datetime.time(3,10,0)
                hold6 = self.is_time_in_range(start6,end6,now_time)                
                
          
                if hold1 or hold2 or hold3 or hold4 or hold5 or hold6  :
                      run = False
                      self.hold_status()
                else:
                      run = True
                      self.run_status()                
                            
                
                print("start up run=",hold1,hold2,hold3,hold4,hold5,hold6)


             if Puasa:
                #shift1
                start1 = datetime.time(10,0,0)  #hold
                end1 = datetime.time(10,10,0)                                
                hold1 = self.is_time_in_range(start1,end1,now_time)

                start2 = datetime.time(12,0,0) #hold
                end2 = datetime.time(13,0,0)
                hold2 = self.is_time_in_range(start2,end2,now_time)

                start3 = datetime.time(14,30,0)  #hold
                end3 = datetime.time(14,40,0)
                hold3 = self.is_time_in_range(start3,end3,now_time)

                #shift 2
                start4 = datetime.time(22,0,0)  #hold
                end4 = datetime.time(22,10,0)
                hold4 = self.is_time_in_range(start4,end4,now_time)

                start5 = datetime.time(0,0,0)  #hold
                end5 = datetime.time(0,30,0)
                hold5 = self.is_time_in_range(start5,end5,now_time)

                start6 = datetime.time(2,0,0)  #hold
                end6 = datetime.time(2,10,0)
                hold6 = self.is_time_in_range(start6,end6,now_time)

                start7 = datetime.time(3,30,0)  #hold
                end7 = datetime.time(4,0,0)
                hold7 = self.is_time_in_range(start7,end7,now_time)               
                
          
                if hold1 or hold2 or hold3 or hold4 or hold5 or hold6 or hold7 :
                      run = False
                      self.hold_status()
                else:
                      run = True
                      self.run_status()
                
                print("start up run=",hold1,hold2,hold3,hold4,hold5,hold6 , hold7)                
                

          #schedule.every(1).hours.do(self.logging_andon)

          #schedule.every().wednesday.at("23:15").do(self.reboot)  




          if not Puasa : #False
                #RESET SCHEDULE
                
                schedule.every().monday.at("7:59").do(self.reset_all)

                schedule.every().tuesday.at("7:59").do(self.reset_all)

                schedule.every().wednesday.at("7:59").do(self.reset_all)

                schedule.every().thursday.at("7:59").do(self.reset_all)

                schedule.every().friday.at("7:44").do(self.reset_all)  #RESET FRIDAY

                schedule.every().saturday.at("7:59").do(self.reset_all)
       
                schedule.every().day.at("19:59").do(self.reset_all)  #RESET AWAL SHIFT 2


                #FRIDAY RUN/HOLD STATUS

                schedule.every().day.at("7:45").do(self.run_status)    #RUN SHIFT 1

                schedule.every().day.at("8:00").do(self.run_status)    #RUN SHIFT 1                

                schedule.every().friday.at("10:00").do(self.hold_status)
                schedule.every().friday.at("10:10").do(self.run_status)

                schedule.every().friday.at("11:30").do(self.hold_status)
                schedule.every().friday.at("13:00").do(self.run_status)

                schedule.every().monday.at("12:00").do(self.hold_status)
                schedule.every().monday.at("13:00").do(self.run_status)
                
                schedule.every().tuesday.at("12:00").do(self.hold_status)
                schedule.every().tuesday.at("13:00").do(self.run_status)


                schedule.every().wednesday.at("12:00").do(self.hold_status)
                schedule.every().wednesday.at("13:00").do(self.run_status)


                schedule.every().thursday.at("12:00").do(self.hold_status)
                schedule.every().thursday.at("13:00").do(self.run_status)

                schedule.every().saturday.at("12:00").do(self.hold_status)
                schedule.every().saturday.at("13:00").do(self.run_status)                
                
                
                
                schedule.every().day.at("15:00").do(self.hold_status)
                schedule.every().day.at("15:10").do(self.run_status)

               
                schedule.every().day.at("22:00").do(self.hold_status)
                schedule.every().day.at("22:10").do(self.run_status)

                schedule.every().day.at("00:00").do(self.hold_status)
                schedule.every().day.at("01:00").do(self.run_status)                
               
                schedule.every().day.at("03:00").do(self.hold_status)
                schedule.every().day.at("03:10").do(self.run_status)              

               
          if Puasa : #True
                #RESET SCHEDULE

                schedule.every().day.at("6:59").do(self.reset_all)   #RESET AWAL SHIFT 1    

                schedule.every().day.at("17:59").do(self.reset_all)  #RESET AWAL SHIFT 2


                #FRIDAY RUN/HOLD STATUS

                schedule.every().day.at("7:00").do(self.run_status)    #RUN SHIFT 1

                schedule.every().day.at("10:00").do(self.hold_status)
                schedule.every().day.at("10:10").do(self.run_status)

                schedule.every().friday.at("11:30").do(self.hold_status)
                schedule.every().friday.at("13:00").do(self.run_status)

               
                schedule.every().monday.at("12:00").do(self.hold_status)
                schedule.every().monday.at("13:00").do(self.run_status)                

                schedule.every().tuesday.at("12:00").do(self.hold_status)
                schedule.every().tuesday.at("13:00").do(self.run_status)

                schedule.every().wednesday.at("12:00").do(self.hold_status)
                schedule.every().wednesday.at("13:00").do(self.run_status)


                schedule.every().thursday.at("12:00").do(self.hold_status)
                schedule.every().thursday.at("13:00").do(self.run_status)

                schedule.every().saturday.at("12:00").do(self.hold_status)
                schedule.every().saturday.at("13:00").do(self.run_status)
                
                               
                schedule.every().day.at("14:30").do(self.hold_status)
                schedule.every().day.at("14:40").do(self.run_status)

                schedule.every().day.at("16:00").do(self.hold_status)
                schedule.every().day.at("16:10").do(self.run_status)

                
                schedule.every().day.at("18:00").do(self.run_status)   #RUN SHIFT 2
                

                schedule.every().day.at("22:00").do(self.hold_status)
                schedule.every().day.at("22:10").do(self.run_status)

                schedule.every().day.at("00:00").do(self.hold_status)
                schedule.every().day.at("00:30").do(self.run_status)                
               
                schedule.every().day.at("02:00").do(self.hold_status)
                schedule.every().day.at("02:10").do(self.run_status)

                schedule.every().day.at("03:30").do(self.hold_status)  #SAHUR
                schedule.every().day.at("04:00").do(self.run_status)
                
                schedule.every().day.at("05:00").do(self.hold_status)  
                schedule.every().day.at("05:10").do(self.run_status)


          
'''




"""
          schedule.every(1).seconds.do(job)
          schedule.every().hour.do(job)
          schedule.every().day.at("10:30").do(job)
          schedule.every().monday.do(job)
          schedule.every().wednesday.at("13:15").do(job)
          schedule.every().sunday.at("07:37").do(job)
          
"""

          
