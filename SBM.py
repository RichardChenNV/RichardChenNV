import random
import time
import PySimpleGUI as sg
import RPi.GPIO as GPIO

SENSOR_GPIO = 16
RESET_GPIO = 23
strike_num = 0
strike_count = 0

def time_as_int():
    return int(round(time.time() * 100))

sg.ChangeLookAndFeel('GreenTan')

def sensor_pressed_callback(channel):
    global strike_num
    global strike_count
    if strike_num > 0:
        strike_num = strike_num - 1
        strike_count = strike_count + 1
        
def reset_button_pressed_callback(channel):
    global strike_num
    strike_num = random.randint (1, 10)

# ------ Column Definition ------ #

col1 = sg.Col([[sg.Text('0', size=(5, 0), auto_size_text=True,justification='center', font=("Helvetica", 60), relief=sg.RELIEF_RAISED, key='Strike_Count',pad=(60,20))]], size=(350,150), pad=(0,0))
col2 = sg.Col([[sg.Text('0', size=(5, 0), justification='center', font=("Helvetica", 60), relief=sg.RELIEF_RIDGE, key='Strike_Num', pad=(60,20))]], size=(350,150), pad=(0,0))
col3 = sg.Col ([
    [sg.Text('', pad=(5,5))],
    [sg.Text('', size=(20, 2), font=('Helvetica', 20),justification='center', key='timer')],
    ])

layout = [
     [sg.Text('Southrac Boxing Machine', size=(150, 1), justification='center', font=("Helvetica", 35), relief=sg.RELIEF_FLAT, key='BoxMachine', pad=(10,20))],
     [sg.Frame('Total Strikes',[[col1]],title_color='red',title_location='n', font=("Helvetica", 25), pad=(50,30)), sg.Frame('Count Down Meter',[[col2]], title_color='blue',title_location='n', font=("Helvetica", 25), pad=(50,30))],
     [sg.Button('squats'), sg.Button('Stop'),sg.Exit()],
     [sg.Frame('Session Timer',[[col3]],title_color='Green',title_location='n', font=("Helvetica", 25), pad=(300,30))],
    ]

window = sg.Window('Southrac Boxing Machine', layout, size = (1024, 800),  default_element_size=(40, 1), grab_anywhere=False)

random.seed ()
current_time, paused_time, timer_stopped = 0, 0, True
start_time = time_as_int()

#Set up the sensor/buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(SENSOR_GPIO, GPIO.RISING,callback=sensor_pressed_callback, bouncetime=100)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(RESET_GPIO, GPIO.RISING,callback=reset_button_pressed_callback, bouncetime=300)


event, values = window.read(timeout=1)
current_time = 0
window.Element('timer').Update('{:02d}:{:02d}.{:02d}'.format((current_time // 100) // 60,
                                    (current_time // 100) % 60,
                                    current_time % 100))
while True:
    
    if timer_stopped != True:
        event, values = window.read(timeout=10)
        current_time = time_as_int() - start_time
    else:
        event, values = window.read()
 
    if event is None or event == 'Exit':
        break
    if event == 'squats':
        #reset the accumulated strikes
        strike_count = 0;
        #Generate a random number
        strike_num = random.randint (1, 10)
        # Start the timer
        timer_stopped = False
        start_time = time_as_int()
    if event == 'Stop':
        timer_stopped = True
    #if event == 'Reset':
    #    strike_num = random.randint (1, 10)

    if timer_stopped != True:
        current_time = time_as_int() - start_time
        window.Element('timer').Update('{:02d}:{:02d}.{:02d}'.format((current_time // 100) // 60,
                                                    (current_time // 100) % 60,
                                                    current_time % 100))
        
    #alway update the counter down meter
    window.Element('Strike_Num').Update(strike_num)
    window.Element('Strike_Count').Update(strike_count)
        
window.close()


