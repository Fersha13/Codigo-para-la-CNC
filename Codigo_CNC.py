import serial
import time
from threading import Event

BAUD_RATE = 115200

'''
Para esta función se trata de en la busqueda de un punto y coma, en la busqueda
de comentarios para estos ser removidos.
'''
def remove_comment(string):
    if string.find(';') == -1:
        return string
    else:
        return string[:string.index(';')]

'''
Esta función trata de eliminar los saltos de linea o espcios sobrantes que se 
encuentran. 
'''
def remove_eol_chars(string):
    return string.strip()

'''
Esta funcion se encarga propiamente de buscar y enlazarse con el puerto serial 
y poner el mensaje inicial en dicho puerto.
'''

def send_wake_up(ser):
    ser.write(str.encode("\r\n\r\n"))
    time.sleep(2)
    ser.flushInput()

'''
Esta funcion se encarga de la lectura y espera de algun movimiento enviado desde
el puerto serial y esta constantemente esperando mediante la lógica, la lectura 
de algun movimiento para posteriormente ser enviado.
'''

def wait_for_movement_completion(ser, cleaned_line):
    Event().wait(1)

    if cleaned_line != '$X' or '$$':

        idle_counter = 0

        while True:

            ser.reset_input_buffer()
            command = str.encode('?' + '\n')
            ser.write(command)
            grbl_out = ser.readline()
            grbl_response = grbl_out.strip().decode('utf-8')

            if grbl_response != 'ok':

                if grbl_response.find('Idle') > 0:
                    idle_counter += 1

            if idle_counter > 10:
                break
    return


def stream_gcode(GRBL_port_path, gcode_path):
    # con contect se abre el archivo/conexion y la cierra si se ha ido la function scope
    with open(gcode_path, "r") as file, serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_wake_up(ser)
        for line in file:
            # se limpia el gcode del archivo
            cleaned_line = remove_eol_chars(remove_comment(line))
            if cleaned_line:  # se revisa que el string este vacio
                print("Sending gcode:" + str(cleaned_line))
                # convierte de un codificado string a byte a string agregandosele una nueva linea
                command = str.encode(line + '\n')
                ser.write(command)  # Envia g-code

                wait_for_movement_completion(ser, cleaned_line)

                grbl_out = ser.readline()  # Espera para respuesta con carga
                print(" : ", grbl_out.strip().decode('utf-8'))

        print('End of gcode')

'''
Se hace la función main 
'''

if __name__ == "__main__":
    # GRBL_port_path = '/dev/tty.usbserial-A906L14X'
    GRBL_port_path = 'Puerto'
    gcode_path = "Localizacion"

    print("USB Port: ", GRBL_port_path)
    print("Gcode file: ", gcode_path)
    stream_gcode(GRBL_port_path, gcode_path)

    print('EOF')