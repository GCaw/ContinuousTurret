import threading
from Tkinter import *
from datetime import datetime
import serial
import sys

global close
close = False
        
def quit_cmd():
	print "QUIT NAOW"
	f.close()

def serialConnect():
	# configure the serial connections (the parameters differs on the device you are connecting to)
	global ser
	ser = serial.Serial(
		#port='/dev/ttyACM0', #This is the form of the port in Linux
                port=3, #port 0 = COM1, port 3 = COM4 etc.
		baudrate=19200,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS
	)
	
	#ser.open() #This line must be uncommented in Linux
	
	ser.isOpen()
	print "Serial On"
	dt1 = datetime.now()
	dt2 = datetime.now()
	while ((dt2.second - dt1.second) < 1):
		dt2 = datetime.now()

	t1 = SerialUpdate()
	t1.start()


def string2bytes (angle, anglei, pos):
	ang =  bin(int(angle))
	lengt = len(bin(int(angle)))

	byt1 = "0"
	byt2 = "0"
	byt3 = "0"
	byt4 = "0"

	byt1 = '000000';

	if (int(angle) == 0):
		byt2 = '0000'

	if (int(angle) >0):
		byt2 =  '000' + str(ang[lengt-1:])

	if (int(angle) >1):
		byt2 =  '00' + str(ang[lengt-2:])

	if (int(angle) >3):
		byt2 =  '0' + str(ang[lengt-3:])

	if (int(angle) >7):
		byt2 =  str(ang[lengt-4:])

	if (int(angle) >15):
		byt1 =  '00000' + str(ang[lengt-5:lengt-4])

	if (int(angle) >31):
		byt1 = '0000' + str(ang[lengt-6:lengt-4])

	if ((int(angle) >63)):
		byt1 = '000' + str(ang[lengt-7:lengt-4])

	if ((int(angle) >127)):
		byt1 = '00' + str(ang[lengt-8:lengt-4])

	if ((int(angle) > 255)):
		byt1 = '0' + str(ang[lengt-9:lengt-4])

	if (int(angle) > 511):
		byt1 = str(ang[lengt-10:lengt-4])

	angle = anglei
	ang =  bin(int(angle))
	lengt = len(bin(int(angle)))

	byt3 = '000';
	if (int(angle) == 0):
		byt4 = '0000000'

	if (int(angle) >0):
		byt4 =  '000000' + str(ang[lengt-1:])

	if (int(angle) >1):
		byt4 =  '00000' + str(ang[lengt-2:])

	if (int(angle) >3):
		byt4 =  '0000' + str(ang[lengt-3:])

	if (int(angle) >7):
		byt4 =  '000' + str(ang[lengt-4:])

	if (int(angle) >15):
		byt4 = '00' + str(ang[lengt-5:])

	if (int(angle) >31):
		byt4 = '0' + str(ang[lengt-6:])

	if ((int(angle) >63)):
		byt4 = str(ang[lengt-7:])

	if ((int(angle) >127)):
		byt3 = '00' + str(ang[lengt-8:lengt-7])

	if ((int(angle) > 255)):
		byt3 = '0' + str(ang[lengt-9:lengt-7])

	if (int(angle) > 511):
		byt3 = str(ang[lengt-10:lengt-7])

	if (pos == 1):
		byt1 = '1'+'1'+byt1
	else:
		byt1 = '1'+'0'+byt1

	byt2 = '0' + byt2+byt3
	byt3 =  '0' + byt4

	#print byt1
	#print byt2
	#print byt3

	return chr(int(byt1,2)), chr(int(byt2,2)), chr(int(byt3,2))

def serial_send_spd():
	b1, b2, b3 = string2bytes (tilt_speed_ach.get(), pan_speed_ach.get(), 0)

	ser.write(b1)
	ser.write(b2)
	ser.write(b3)

def serial_send_pos():
	b1, b2, b3 = string2bytes (tilt_ach.get(), pan_ach.get(), 1)

	ser.write(b1)
	ser.write(b2)
	ser.write(b3)

class SerialUpdate(threading.Thread):
	def run(self):
		global f
		j = 0
		f = open('log1.csv', 'w')
		out = 2
		out2 = 2
		print "yes this is on"

		while True:
			out = long(ord(ser.read(1)))
			dt3 = datetime.now()
			if out != '':
				if out > 127:
					#check if sensor 1 or 2
					out2 = long(ord(ser.read(1)))
					f.write(str(long(dt3.microsecond/1000))+',')
					f.write(str(out) + ',')
					f.write(str(out2) + ',')

					if (out - 128) > 63:
						#sensor 1
						
						if (out - 128 - 64) > 31:
							#update sensor 1 value
							f.write('sensor 1,')
							if (out - 128-64-32) > 7:
								sens1.set("error")
							else:
								sens1.set(str(out2 + ((out-128-64-31)*(2**7)-128)))
							f.write(sens1.get() + ',')
						else:
							#update counter 1 value
							f.write('counter 1,')
							count1.set(str(out2 + (out-128-64)*(2**7)))
							f.write(count1.get() + ',')
					else:
						#sensor 2

						if (out - 128) > 31:
							f.write('sensor 2,')
							if (out - 128-32) > 7:
								sens2.set("error")
							else:
								sens2.set(str(out2 + (out-128-31)*(2**7)-128))
							f.write(sens2.get() + ',')
						else:
							f.write('counter 2,')	
							#update counter 2 value
							count2.set(str(out2 + (out-128)*(2**7)))
							f.write(count2.get() + ',')
					j+=1
					if (j < 4):
						f.write(',')
					else:
						f.write(pan_ach.get()+ ','+ tilt_ach.get() + ',' +pan_speed_ach.get() + ',' + tilt_speed_ach.get()+'\n');				
						j=0

class GUI(threading.Thread):
	def run(self):
		global root
		root = Tk()

		def go_pos():
			print "Go to place"
			pan_ach.set(pan_new.get())
			pan_new.delete(0,END)
			tilt_ach.set(tilt_new.get())
			tilt_new.delete(0,END)
			serial_send_pos()

		def go_speed():
			print "Go @ speed"
			pan_speed_ach.set(pan_new_speed.get())
			pan_new_speed.delete(0,END)
			tilt_speed_ach.set(tilt_new_speed.get())
			tilt_new_speed.delete(0,END)
			serial_send_spd()

		def stop_pos():
			print "STOP"
			pan_speed_ach.set(0)
			tilt_speed_ach.set(0)
			serial_send_spd()
		

		def hello():
			print "hello!"

		def serialDConnect():
			ser.close()
			print "Serial Off"

		def serialRead():
			while ser.inWaiting() > 0:
				print ser.read(1)
			print "ll"

		global pan_ach
		pan_ach = StringVar()
		global tilt_ach
		tilt_ach = StringVar()
		global pan_speed_ach
		pan_speed_ach = StringVar()
		global tilt_speed_ach
		tilt_speed_ach = StringVar()	

		global sens1
		sens1 = StringVar()
		sens1.set(0)
		global sens2
		sens2 = StringVar()
		sens2.set(0)
		global spd1
		spd1 = StringVar()
		spd1.set(0)
		global spd2
		spd2 = StringVar()
		spd2.set(0)

		global count1
		count1 = StringVar()
		count1.set(0)
		global count2
		count2 = StringVar()
		count2.set(0)
		global counts1
		counts1 = StringVar()
		counts1.set(0)
		global counts2
		counts2 = StringVar()
		counts2.set(0)

		count1_val = Label(textvariable=count1);
		count2_val = Label(textvariable=count2);
		counts1_val = Label(textvariable=counts1);
		counts2_val = Label(textvariable=counts2);

		Label(text="Position").grid(row=0, sticky=W)
		Label(text="Pan: ").grid(row=1, sticky=W)
		Label(text="Tilt: ").grid(row=2, sticky=W)
		Label(text="Speed").grid(row=4, sticky=W)

		Label(text="Pan: ").grid(row=5, sticky=W)
		Label(text="Tilt: ").grid(row=6, sticky=W)

		pan_val = Label(textvariable=sens1)
		tilt_val = Label(textvariable=sens2)
		pan_speed = Label(textvariable=spd1)
		tilt_speed = Label(textvariable=spd2)
		aim = Label(text="Aim")
		sens = Label(text="Sensors")
		count = Label(text="Count")
		pan_val_ach = Label(textvariable=pan_ach);    
		tilt_val_ach = Label(textvariable=tilt_ach);
		pan_val_speed_ach = Label(textvariable=pan_speed_ach);    
		tilt_val_speed_ach = Label(textvariable=tilt_speed_ach);

		pan_ach.set(0)
		tilt_ach.set(0)
		pan_speed_ach.set(0)
		tilt_speed_ach.set(0)
		global pan_new
		pan_new = Entry()
		global tilt_new
		tilt_new = Entry()
		global pan_new_speed
		pan_new_speed = Entry()
		global tilt_new_speed
		tilt_new_speed = Entry()

		go_but = Button(text="Go", command=go_pos)
		go_but2 = Button(text="Go", command=go_speed)
		stop_but = Button(text="STOP", command=stop_pos)
		quit_but = Button(text="QUIT", fg="red", command=quit_cmd)

		pan_new.grid(row=1, column=1)
		pan_val.grid(row=1, column=3, sticky=W)

		tilt_new.grid(row=2, column=1)
		tilt_val.grid(row=2, column=3, sticky=W)
	
		pan_new_speed.grid(row=5, column=1)
		pan_speed.grid(row=5, column=3)
		tilt_new_speed.grid(row=6, column=1)
		tilt_speed.grid(row=6, column=3)        

		aim.grid(row=0,column=2)

		pan_val_ach.grid(row=1, column=2)
		tilt_val_ach.grid(row=2, column=2)

		pan_val_speed_ach.grid(row=5, column=2)
		tilt_val_speed_ach.grid(row=6, column=2)

		go_but.grid(row=3)
		go_but2.grid(row=7)
		stop_but.grid(row=9)
		quit_but.grid(row=9, column=1)

		sens.grid(row=0, column=3)
		count.grid(row=0, column=4)
		count1_val.grid(row=2, column=4)
		count2_val.grid(row=1, column=4)
		counts1_val.grid(row=6, column=4)
		counts2_val.grid(row=5, column=4)

		menubar = Menu(root)

		# create a pulldown menu, and add it to the menu bar
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Open", command=hello)
		filemenu.add_command(label="Save", command=hello)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=quit_cmd)
		menubar.add_cascade(label="File", menu=filemenu)

		# create more pulldown menus
		serialmenu = Menu(menubar, tearoff=0)

		windowsmenu = Menu(serialmenu,tearoff=0)
		windowsmenu.add_radiobutton(label="COM1", command=hello)
		windowsmenu.add_radiobutton(label="COM2", command=hello)
		windowsmenu.add_radiobutton(label="COM3", command=hello)
		windowsmenu.add_radiobutton(label="COM4", command=hello)
		serialmenu.add_cascade(label="Windows", menu=windowsmenu)

		linuxmenu=Menu(serialmenu,tearoff=0)
		linuxmenu.add_radiobutton(label="ttyS0", command=hello)
		linuxmenu.add_radiobutton(label="ttyS1", command=hello)
		linuxmenu.add_radiobutton(label="ttyS2", command=hello)
		linuxmenu.add_radiobutton(label="ttyS3", command=hello)
		linuxmenu.add_radiobutton(label="ttyACM0", command=hello)
		linuxmenu.add_radiobutton(label="ttyACM1", command=hello)
		serialmenu.add_cascade(label="Linux", menu=linuxmenu)

		serialmenu.add_separator()
		serialmenu.add_command(label="Connect", command=serialConnect)
		serialmenu.add_command(label="Disconnect", command=serialDConnect)
		menubar.add_cascade(label="Serial", menu=serialmenu)

		helpmenu = Menu(menubar, tearoff=0)
		helpmenu.add_command(label="About", command=hello)
		menubar.add_cascade(label="Help", menu=helpmenu)

		# display the menu
		root.config(menu=menubar)

		root.mainloop()


t2 = GUI()
t2.start()

