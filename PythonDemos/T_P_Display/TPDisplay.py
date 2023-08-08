import serial
import pygame
import sys

# set up the serial line
#ser = serial.Serial('/dev/ttyUSB0', 9600)  # Change with actual serial port and baud rate
ser = serial.Serial('COM19',9600)

# initialize pygame and setup display parameters
pygame.init()
screen = pygame.display.set_mode((800, 600))  # Change this to match your screen resolution
font = pygame.font.Font(None, 72)  # You can change the font size here

def display_text(text, position):
    surface = font.render(text, True, (255, 255, 255))  # Render the text
    rect = surface.get_rect(center=position)  # Get the rectangle for positioning
    screen.blit(surface, rect)  # Display the text

while True:
    try:
        # read the data from the serial port
        data = ser.readline().decode('utf-8').strip()
        temperature, pressure = data.split(',')
        
        # print it in console
        print(f"Temperature: {temperature}, Pressure: {pressure}")

        # update the display
        screen.fill((0, 0, 0))  # Clear the screen
        display_text(f"Temperature: {temperature}", (400, 200))  # Adjust position as needed
        display_text(f"Pressure: {pressure}", (400, 400))  # Adjust position as needed
        pygame.display.flip()  # Update the display

        # quit the program on a quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
    except ValueError:
        # If the data received does not unpack into temperature and pressure, skip it.
        pass
    except serial.SerialException:
        # If any other Serial error occurs, print it and exit.
        print('Serial Error', sys.exc_info()[0])
        break
