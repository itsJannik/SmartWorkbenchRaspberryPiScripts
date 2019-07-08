#! /usr/bin/python3
import getopt, json, ssl, sys, time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

PORT = 8883
BROKER = ""
TOPIC_TO_PUBLISH   = "smw/workbench_1/pi_2/pir"
TOPIC_TO_SUBSCRIBE = "smw/workbench_1/pi_2/led"
PAYLOAD  = json.dumps({'motionDetected': True})
USERNAME = ""
PASSWORD = ""

mqtt.Client.connected_flag = False
mqtt.Client.bad_connection_flag = False

def create_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_insecure_set(False)
    client.username_pw_set(username=USERNAME, password=PASSWORD)
    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag=True
        print("connected OK Returned code =",rc)        
        subscribe_to_topic(client, TOPIC_TO_SUBSCRIBE)
    else:
        print("[ERROR] Bad connection Returned code =",rc)
        client.bad_connection_flag = True

def on_message(client, userdata, message):
    print("message received")
    print("message received", str(message.payload.decode("utf-8")))
    turn_the_lights_on(json.loads(str(message.payload.decode("utf-8"))))

def connect_to_broker(client, host=BROKER, port=PORT):
    print("Connecting to broker ", BROKER)
    try:
        client.connect(host=BROKER, port=PORT, keepalive=10)
    except Exception as e:
        print("[ERROR] connection to Broker failed, error: {}".format(e))
    client.loop_start()
    while not client.connected_flag and not client.bad_connection_flag: 
        print("In wait loop, not connected yet")
        time.sleep(0.5)
    if client.bad_connection_flag:
        client.loop_stop()
        client.disconnect()
        print("[ERROR] Bad connection disconnect from broker")

def publish_payload(client, topic=TOPIC_TO_PUBLISH, payload=PAYLOAD):
    if client.connected_flag and not client.bad_connection_flag:
        try:
            client.publish(topic=topic, payload=payload, qos=2)
        except Exception as e:
            print("[ERROR] Could not publish data, error: {}".format(e))
    else:
        print("[ERROR] Publishing filed, client not connected or bad connection")

def subscribe_to_topic(client, topic=TOPIC_TO_SUBSCRIBE):
    print("subscribing to ", topic)
    try:
        client.subscribe(topic=topic, qos=2)
    except Exception as e:
        print("[ERROR] Could not subscribe: {}".format(e))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
PIR_PIN = 7
RED_PIN = 33
GREEN_PIN = 35
BLUE_PIN = 37

GPIO.setup(PIR_PIN, GPIO.IN)         
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

def turn_on(pin):
    print("turn on", pin)
    turn_off([RED_PIN, GREEN_PIN, BLUE_PIN])
    try:
        GPIO.output(pin, GPIO.HIGH)
        if pin == RED_PIN:
            time.sleep(5)
            GPIO.output(pin, GPIO.LOW)
    except:
        print("error while setting output to high")

def turn_off(pins):
    for pin in pins:
        GPIO.output(pin, GPIO.LOW)
        print("turning off", pin)

def turn_the_lights_on(light):
    print("turn the lights on", light)
    color = light["color"]
    print("color to light", color)
    if color == "red":
        turn_on(RED_PIN)
    elif color == "green":
        turn_on(GREEN_PIN)
    elif color == "blue":
        turn_on(BLUE_PIN)
    else:
        print("[ERROR] Bad Color")

def main(argv):
    #global TOPIC_TO_PUBLISH, TOPIC_TO_SUBSCRIBE
    #try:
    #    opts, args = getopt.getopt(argv,"hp:s:",["p_topic=","s_topic="])
    #except getopt.GetoptError:
    #    print('start.py -p <topic_to_publish> -s <topic_to_subscribe>')
    #    sys.exit(2)
    #for opt, arg in opts:
    #    if opt == '-h':
    #        print('start.py -p <topic_to_publish> -s <topic_to_subscribe>')
    #        sys.exit()
    #    elif opt in ("-p", "--topic_to_publish"):
    #        TOPIC_TO_PUBLISH = arg
    #    elif opt in ("-s", "--topic_to_subscribe"):
    #        TOPIC_TO_SUBSCRIBE = arg
    #print('Topic to Publish ', TOPIC_TO_PUBLISH)
    #print('Topic to Subscribe ', TOPIC_TO_SUBSCRIBE)

    client = create_client()
    connect_to_broker(client)
    #subscribe_to_topic(client, TOPIC_TO_SUBSCRIBE)
    try:
        while True:
            pir_input = GPIO.input(PIR_PIN)
            if pir_input == GPIO.LOW:
                print("No Motion")
                time.sleep(0.5)
            elif pir_input == GPIO.HIGH:
                print("Motion  detected")
                publish_payload(client, topic=TOPIC_TO_PUBLISH)
                #publish_payload(client, topic="smw/workbench_1/pi_2/pir")
                #Since the output stays high for ~1.3/3 s after detecting motion
                #Since the output stays low for ~3 s after that
                #this 'long' time prohibits multiple HIGHs
                time.sleep(6.5)
    except Exception:
        GPIO.cleanup()

if __name__ == "__main__":
    main(sys.argv[1:])
