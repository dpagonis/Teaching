import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
import time
import serial
import re
from datetime import datetime

#ser = serial.Serial('/dev/ttyUSB1',9600)




fig = plt.figure()

im = plt.imread('chembio_horiz.png') # insert local path of the image.
ax_logo = fig.add_axes([0,0.78,1,0.2], anchor='N', zorder=1)
ax_logo.imshow(im)
ax_logo.axis('off')


ax_CO2 = fig.add_axes([0.2,0.1,0.7,0.6])

#CO2_ppm = fig.text(0.7,0.3,'XX ppm')

LoopCount = 0
x_time = []
y_CO2=[]

def animate(i):

    try:
        ser = serial.Serial('/dev/ttyUSB1',9600)
        sRaw = str(ser.readline())
        ctime = datetime.now()
        ser.close()
        sOut = re.sub("[^0-9^,^.,^-]", "", sRaw)+"\n" # Use regular expressions to replace all non-numbers (^0-9) and non-commas (^,) with a null string
        spres,sCO2 = sOut.split(',')
        CO2 = float(sCO2) if float(sCO2)>0 else CO2
        pres = float(spres)
        if len(x_time) >= 3600:
            x_time.pop(0)
            y_CO2.pop(0)

        x_time.append(ctime)
        y_CO2.append(CO2)
    except:
        pass

    ax_CO2.clear()
    ax_CO2.plot(x_time,y_CO2)
    ax_CO2.set_xlabel('Time')
    ax_CO2.set_ylabel('CO$_2$ (ppm)')
    ax_CO2.xaxis.set_major_locator(plt.MaxNLocator(4))
    ax_CO2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()

    #sCO2_ppm = 'CO$_2$: %.0f ppm\nPressure: %.01f mbar' % (CO2, pres)
    #CO2_ppm.set_text(sCO2_ppm)

ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()
