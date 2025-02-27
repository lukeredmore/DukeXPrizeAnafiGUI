#!/usr/bin/env python3

# Environment setup commands:
# olympe: source ~/code/parrot-groundsdk/./products/olympe/linux/env/shell
import tkinter as tk
from tkinter import *
from PIL import Image
from PIL import ImageTk
import olympe
import subprocess
import time
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, PCMD
from collections import defaultdict
from olympe.messages.ardrone3.PilotingSettingsState import MaxTiltChanged
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
import olympe.messages.gimbal as gimbal


import os
import pprint
import pygame



# from enum import Enum

# Drone flight state variables
is_connected = False
gimbal_attitude = 0
horzScalingFactor = 10
vertScalingFactor = 10

p1 = subprocess;

# Drone constants
DRONE_IP = "192.168.42.1"
SPHINX_IP = "10.202.0.1"

# UI Global variables
HEIGHT = 750
WIDTH = 830
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50
ROTATE_BUTTON_WIDTH = 70
ROTATE_BUTTON_HEIGHT = 400

# Control variables
control_quit = 0
control_takeoff = 1

# Button helper functions
# Roll drone to the left 
def roll_left():
    drone(
        PCMD(
            1,
            -10,
            0,
            0,
            0,
            10,
        )
    ) 

# Roll drone to the right 
def roll_right():
    drone(
        PCMD(
            1,
            10,
            0,
            0,
            0,
            10,
        )
    )

# Pitch the drone forward (move forward)
def pitch_fwd():
    drone(
        PCMD(
            1,
            0,
            10,
            0,
            0,
            10,
        )
    )

# Pitch drone backward (move backward)
def pitch_back():
    drone(
        PCMD(
            1,
            0,
            -10,
            0,
            0,
            10,
        )
    )

# Spin drone to the left 
def turn_left():
    display_message('Turning left...')
    drone(
        PCMD(
            1,
            0,
            0,
            -10,
            0,
            10,
        )
    )

# Turn drone to the right
def turn_right():
    display_message('Turning right...')
    drone(
        PCMD(
            1,
            0,
            0,
            10,
            0,
            10,
        )
    )

def increase_throttle():
    drone(
        PCMD(
            0,
            0,
            0,
            0,
            10,
            10,
        )
    )

def decrease_throttle():
    drone(
        PCMD(
            0,
            0,
            0,
            0,
            -10,
            10,
        )
    )


def move_drone(rollVal=0, pitchVal=0, spinVal=0, throttleVal=0):
    drone(
        PCMD(
            1,
            int(rollVal),      # roll (negative means left, positive means right)
            int(pitchVal),     # pitch (negative means back, positive means forward)
            int(spinVal),      # yaw (negative means turn left, positive means turn right)
            int(throttleVal),  # power (negative means descend, positive means ascend)
            1,
        )
    )




# Connect to drone
def connect():
    global is_connected
    if not is_connected:
        display_message('Connecting to the drone...')
        if(not drone.connect()):
            display_message('Connection failed.')
            is_connected = False
            return False
        display_message('Connected successfully.')
        is_connected = True
        enable_gimbal_buttons()
    else:
        land()
        display_message("Disconnecting from the drone...")
        if drone.disconnect():
            is_connected = False
            display_message("Disonnected succesfully")
            disable_gimbal_buttons()
    
    start_fpv_button.config(state = "normal")

    

# Takeoff routine
def takeoff():
    display_message('Taking off...')
    if not drone(TakeOff()).wait().success():
        display_message('Failed to takeoff')
        return False
    display_message('Takeoff successful')
    # Set gimbal to attitude so that it looks straight
    drone(
        gimbal.set_target(
            gimbal_id = 0,
            control_mode = "position",
            yaw_frame_of_reference = "absolute",
            yaw = 0.0,
            pitch_frame_of_reference = "absolute",
            pitch = 0,
            roll_frame_of_reference = "absolute",
            roll = 0.0
        )
    ).wait()
    global gimbal_attitude
    gimbal_attitude = 0.0

    takeoff_button.config(state = "disabled")
    enable_movement_buttons()

# Landing routine
def land():
    display_message('Landing...')
    if not drone(Landing()).wait().success():
        display_message('Failed to land')
        return False
    display_message('Landed successfully.')
    disable_all_buttons()
    enable_gimbal_buttons()

def move_forward():
    global gimbal_attitude
    
    # Move straight 
    if gimbal_attitude <= 10 and gimbal_attitude >= -10:
        display_message('Moving straight forward.')
        pitch_fwd()
    # Increase throttle - move up
    elif gimbal_attitude == 100:
        display_message('Increasing throttle.')
        increase_throttle()
    # Decrease throttle - move down
    elif gimbal_attitude == -100:
        display_message('Decreasing throttle.')
        decrease_throttle()
    
def move_gimbal(attitude):
    drone(
        gimbal.set_target(
            gimbal_id = 0,
            control_mode = "position",
            yaw_frame_of_reference = "absolute",
            yaw = 0.0,
            pitch_frame_of_reference = "absolute",
            pitch = attitude,
            roll_frame_of_reference = "absolute",
            roll = 0.0
        )
    ).wait()

def gimbal_up():
    global gimbal_attitude
    new_attitude = gimbal_attitude + 10

    if new_attitude > 100:
        new_attitude = 100

    display_message('Tilting gimbal up.')
    move_gimbal(new_attitude)

    gimbal_attitude = new_attitude

    if gimbal_attitude != 100:
        takeoff_button.config(state = "disabled")
    else:
        takeoff_button.config(state = "normal")

    land_button.config(state = "disabled")


def gimbal_up(attitude):
    global gimbal_attitude
    new_attitude = gimbal_attitude + attitude

    if new_attitude > 100:
        new_attitude = 100

    display_message('Tilting gimbal up.')
    move_gimbal(new_attitude)

    gimbal_attitude = new_attitude

    if gimbal_attitude != 100:
        takeoff_button.config(state = "disabled")
    else:
        takeoff_button.config(state = "normal")

    land_button.config(state = "disabled")

def gimbal_down():
    global gimbal_attitude
    new_attitude = gimbal_attitude - 10

    if new_attitude < -100:
        new_attitude = -100

    display_message('Tilting gimbal down')
    move_gimbal(new_attitude)

    gimbal_attitude = new_attitude
    
    if gimbal_attitude != -100:
        land_button.config(state = "disabled")
    else:
        land_button.config(state = "normal")

    takeoff_button.config(state = "disabled")

def gimbal_down(attitude):
    global gimbal_attitude
    new_attitude = gimbal_attitude - attitude

    if new_attitude < -100:
        new_attitude = -100

    display_message('Tilting gimbal down')
    move_gimbal(new_attitude)

    gimbal_attitude = new_attitude
    
    if gimbal_attitude != -100:
        land_button.config(state = "disabled")
    else:
        land_button.config(state = "normal")

    takeoff_button.config(state = "disabled")

def look_forward():
    global gimbal_attitude
    
    move_gimbal(0)
    display_message('Gimbal facing straight ahead.')

    gimbal_attitude = 0

    takeoff_button.config(state = "disabled")
    land_button.config(state = "disabled")

def look_up():
    global gimbal_attitude

    move_gimbal(100)
    display_message('Gimbal facing straight up.')

    gimbal_attitude = 100

    takeoff_button.config(state = "normal")
    land_button.config(state = "disabled")

def look_down():
    global gimbal_attitude

    move_gimbal(-100)
    display_message('Gimbal facing straight down.')

    gimbal_attitude = -100

    takeoff_button.config(state = "disabled")
    land_button.config(state = "normal")
    
def start_fpv():
    display_message('Starting first person view video feed...')
    #p1 = subprocess.Popen(['/home/achilles/code/parrot-groundsdk/out/pdraw-linux/staging/native-wrapper.sh', 'pdraw', '-u','rtsp://10.202.0.1/live'])
    p1 = subprocess.Popen(['/home/drone/Desktop/groundsdk-tools/out/groundsdk-linux/staging/native-wrapper.sh', 'pdraw', '-u','rtsp://%s/live' % DRONE_IP])
    
def startController():
    ps4 = PS4Controller()
    ps4.init()
    ps4.listen()
    
    start_controller_button.config(state="normal")

def display_message(message):
    global message_box
    message_box.insert(END, message)

# setting up screen
root = tk.Tk()
root.resizable(False, False)
root.title("Anafi Drone GUI")
root.configure(bg='white')
p1 = PhotoImage(file = 'images/drone.png')
root.iconphoto(False, p1)

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.configure(bg='white')
canvas.pack()

controlFrame = tk.Frame(root)
controlFrame.configure(bg='white')
controlFrame.place(relwidth=.95, relheight=.95, relx=0.025, rely=0.025)

# rotate left
l_rotate_button_image = Image.open("images/turn_left.png")
l_rotate_photoImg = ImageTk.PhotoImage(l_rotate_button_image)
l_rotate_button = Button(controlFrame, image=l_rotate_photoImg, command=turn_left)
l_rotate_button.place(relwidth=.2, relheight=.2105, relx=0, rely=0.35)

# rotate right
r_rotate_button_image = Image.open("images/turn_right.png")
r_rotate_photoImg = ImageTk.PhotoImage(r_rotate_button_image)
r_rotate_button = Button(
    controlFrame, image=r_rotate_photoImg, command=turn_right)
r_rotate_button.place(relwidth=.2, relheight=.2105, relx=0.35, rely=0.35)

# move forward button
forward_button_image = Image.open("images/move_forward.png")
forward_button_photoImg = ImageTk.PhotoImage(forward_button_image)
forward_button = Button(
    controlFrame, image=forward_button_photoImg, command=move_forward)
forward_button.place(relwidth=0.15, relheight=0.2, relx=0.20, rely=0.1)

# connect button
connect_button_image = Image.open("images/connect.png")
connect_button_photoImg = ImageTk.PhotoImage(connect_button_image)
connect_button = Button(
    controlFrame, image=connect_button_photoImg, command=connect)
connect_button.place(relwidth=0.2, relheight=0.1, relx=.56, rely=.58)

# Start FPV button
start_fpv_image = Image.open("images/start_fpv.png")
start_fpv_button_photoImg = ImageTk.PhotoImage(start_fpv_image)
start_fpv_button = Button(
    controlFrame, image=start_fpv_button_photoImg, command=start_fpv)
start_fpv_button.place(relwidth=0.2, relheight=0.1, relx=0.785, rely=.58)

# takeoff button
takeoff_button_image = Image.open("images/takeoff.png")
takeoff_button_photoImg = ImageTk.PhotoImage(takeoff_button_image)
takeoff_button = Button(
    controlFrame, image=takeoff_button_photoImg, command=takeoff)
takeoff_button.place(relwidth=0.22, relheight=0.28, relx=0.55, rely=.7)

# land button
land_button_image = Image.open("images/land.png")
land_button_photoImg = ImageTk.PhotoImage(land_button_image)
land_button = Button(
    controlFrame, image=land_button_photoImg, command=land)
land_button.place(relwidth=0.22, relheight=0.28, relx=0.785, rely=.7)

# gimbal up button
gimbal_up_button_image = Image.open("images/gimbal_up.png")
gimbal_up_button_photoImg = ImageTk.PhotoImage(gimbal_up_button_image)
gimbal_up_button = Button(
    controlFrame, image=gimbal_up_button_photoImg, command=gimbal_up)
gimbal_up_button.place(relwidth=.207, relheight=.2105, relx=0.56, rely=0.1)

# gimbal down button
gimbal_down_button_image = Image.open("images/gimbal_down.png")
gimbal_down_button_photoImg = ImageTk.PhotoImage(gimbal_down_button_image)
gimbal_down_button = Button(
    controlFrame, image=gimbal_down_button_photoImg, command=gimbal_down)
gimbal_down_button.place(relwidth=.207, relheight=.2105, relx=0.56, rely=0.35)

# look up button
look_up_button_image = Image.open("images/look_up.png")
look_up_button_photoImg = ImageTk.PhotoImage(look_up_button_image)
look_up_button = Button(
    controlFrame, image=look_up_button_photoImg, command=look_up)
look_up_button.place(relwidth=.207, relheight=.15, relx=0.785, rely=0.1)

# look forward button
look_forward_button_image = Image.open("images/look_forward.png")
look_forward_button_photoImg = ImageTk.PhotoImage(look_forward_button_image)
look_forward_button = Button(
    controlFrame, image=look_forward_button_photoImg, command=look_forward)
look_forward_button.place(relwidth=.207, relheight=.15, relx=0.785, rely=0.257)

# look down button
look_down_button_image = Image.open("images/look_down.png")
look_down_button_photoImg = ImageTk.PhotoImage(look_down_button_image)
look_down_button = Button(
    controlFrame, image=look_down_button_photoImg, command=look_down)
look_down_button.place(relwidth=.207, relheight=.15, relx=0.785, rely=0.41)

# Controller button
start_controller_button_image = Image.open("images/start_controller.png")
start_controller_button_photoImg = ImageTk.PhotoImage(start_controller_button_image)
start_controller_button = Button(
	controlFrame, image=start_controller_button_photoImg, command=startController)
start_controller_button.place(relwidth=.15, relheight=.15, relx=0.20, rely=0.6)

message_box = Listbox(controlFrame)
message_box.place(relwidth= .5, relheight= .2, relx= 0, rely= .8)



buttons = [ l_rotate_button,
            r_rotate_button, 
            forward_button, 
            takeoff_button,
            land_button,
            gimbal_up_button,
            gimbal_down_button,
            look_up_button,
            look_forward_button,
            look_down_button,
            connect_button,
            start_fpv_button,
            start_controller_button ]

def disable_all_buttons():
    global buttons
    for button in buttons:
        button.config(state = "disabled")

def enable_all_buttons():
    global buttons
    for button in buttons:
        button.config(state = "normal")

def disable_gimbal_buttons():
    look_up_button.config(state = "disabled")
    look_down_button.config(state = "disabled")
    look_forward_button.config(state = "disabled")
    gimbal_up_button.config(state = "disabled")
    gimbal_down_button.config(state = "disabled")

def enable_gimbal_buttons():
    look_up_button.config(state = "normal")
    look_down_button.config(state = "normal")
    look_forward_button.config(state = "normal")
    gimbal_up_button.config(state = "normal")
    gimbal_down_button.config(state = "normal")

def enable_movement_buttons():
    l_rotate_button.config(state = "normal")
    r_rotate_button.config(state = "normal")
    forward_button.config(state = "normal")
    
    
    
# class for the ps4 controller object
class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def init(self):
        """Initialize the joystick components"""
        pygame.init()
        pygame.joystick.init()
        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
        except:
           display_message("Failed to connect to Controller")
        

    def listen(self):
        """Listen for events to happen"""
        global horzScalingFactor
        global vertScalingFactor

        if not self.axis_data:
            self.axis_data = [0,0,0,0,0,0]

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = (0,0)
            # for i in range(self.controller.get_numhats()):
            #     self.hat_data[i] = (0, 0)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = round(event.value,2)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                    
                    # handle single press buttons
                    if is_connected:
                        
                        if event.button == 2:
                            # land
                            land()
                        elif event.button == 3:
                            # takeoff
                            takeoff()
                        elif event.button == 4:
                            l1 = 0
                        elif event.button == 5:
                            r1 = 0
                        elif event.button == 6:
                            start_fpv()
                        elif event.button == 9:
                            l3 = 0
                        elif event.button == 10:
                            r3 = 0
                    if event.button == 7:
                        connect()
                    elif event.button == 8:
                        return

                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data = event.value

                    # Handle hat inputs for adjusting scaling factor
                    if self.hat_data[0] != 0:
                        horzScalingFactor = horzScalingFactor + 10*self.hat_data[0]
                    if self.hat_data[1] !=0:
                        vertScalingFactor = vertScalingFactor + 10*self.hat_data[1]
                    if vertScalingFactor > 100:
                        vertScalingFactor = 100
                    elif vertScalingFactor < 10:
                        vertScalingFactor = 10
                    if horzScalingFactor > 100:
                        horzScalingFactor = 100
                    elif horzScalingFactor < 10:
                        horzScalingFactor = 10

                
            # handle buttons that are held down
            if is_connected:
                
                # handle left joystick input to move drone
                if self.axis_data[0] != 0 or self.axis_data[1] != 0 or self.axis_data[2] > 0 or self.axis_data[5] > 0 or self.button_data[0] != 0 or self.button_data[1] !=0:
                    # send all data from the joystick to the roll / pitch commands
                    throttleInput = -vertScalingFactor * self.button_data[0] + vertScalingFactor * self.button_data[1]
                    
                    # handle trigger inputs to spin drone
                    spinInput = 0
                    if self.axis_data[2] > 0 and self.axis_data[5] > 0:
                        spinInput = 0
                    elif self.axis_data[2] > 0:
                        spinInput = -100*self.axis_data[2]
                    elif self.axis_data[5] > 0:
                        spinInput = 100*self.axis_data[5]
                    
                    move_drone(rollVal=horzScalingFactor*self.axis_data[0], pitchVal=-horzScalingFactor*self.axis_data[1], throttleVal=throttleInput, spinVal=spinInput)
                
                # handle right joystick to move camera up or down
                if self.axis_data[4] < 0:
                    gimbal_up(abs(self.axis_data[4]))
                elif self.axis_data[4] > 0:
                    gimbal_down(abs(self.axis_data[4]))
                            
                # os.system('clear')
                # pprint.pprint(self.button_data)
                # pprint.pprint(self.axis_data)
                # pprint.pprint(self.hat_data)

# Main Loop Start:
if __name__ == "__main__":
    with olympe.Drone(DRONE_IP) as drone:
        disable_all_buttons()
        connect_button.config(state = "normal")
        start_controller_button.config(state="normal")
        root.mainloop()