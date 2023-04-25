
import websocket
import _thread
import time
import re
import rel
from datetime import datetime, timezone


DRONE_ID="1b058a6e5d66031f11f71684b302f51d"
ACCESS_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNpZy1ycy0wIn0.eyJwbGV4Ijp7ImNvbXBhbnlfaWQiOiIxYjA1OGE2ZTVkNjYwMzFmMTFmNzE2ODRiMzAxYTU1YiIsImNsaWVudF9pZCI6IjFiMDU4YTZlNWQ2NjAzMWYxMWY3MTY4NGIzMDFhNTViIn0sImp0aSI6IlVTcHJ3akdzelpqQXdGdnpOWWEyWiIsImlhdCI6MTY4MDY4OTI5MiwiZXhwIjoxNjg4NDY1MjkyLCJpc3MiOiJodHRwczovL2lkZW50aXR5LmdhcnVkYS5pbyIsImF1ZCI6IjFiMDU4YTZlNWQ2NjAzMWYxMWY3MTY4NGIzMDFhNTViIn0.LmgpjNFmojJMMaHu_JT42owVPY9cGBhx8wbxwq88cK_sHUapiYYGJNu5kyJNRWwFOQOi30MlJ7mbeWH1PKLu3_H5SvUpKQtyn8GB7jUabqnLaHLa5Sl76KBhRyP_Zy5YDSu8AqD8HAVh4ON8si-goGmZQXVXmejN12islJvGMdc4DqhKGmQ90T0sVpum51IQAqchKFEtLfhZgQuGsdfQWbyhLTEVQk_DY4pMeRQGfNqA20-IBxbETwccT42zYXYG4XDnUY-UtaFA3BJ9AquXJphc97kTpdPV4uPhosXeoncVTJgWd9CZzg5uPNfPM2yQKoYdb4ZxTZN0qHnSMTMHeA"
WS_URL = f"wss://xprize.mydronefleets.com/live/tracker/netrid/?drone_id={DRONE_ID}&access_token={ACCESS_TOKEN}"

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Connected to telemetry web socket endpoint! Press CTRL+C in this terminal to open the control GUI. (Yes this is a weird bug, someone good at multi-threading should fix it :)")

def send_telemetry(lat_n, lng_e, alt_cm, grounded=True, v_acc=-1, h_acc=-1):
    date_string = datetime.utcnow().isoformat("T") + "Z"
    payload = """{
        "t": "%s",
        "lat": "%s",
        "lng": "%s",
        "alt": %s,
        "status": %s,
        "v_acc": %s,
        "h_acc": %s
    }""" % (date_string, round(lat_n,7), round(lng_e,7), round(alt_cm), 1 if grounded else 2, round(v_acc, 2), round(h_acc, 2))
    print(payload)
    ws.send(payload)

def send_telemetry_init():
    date_string = datetime.utcnow().isoformat("T") + "Z"
    payload = """{
        "t": "%s",
        "lat": "",
        "lng": "",
        "alt": 0,
        "status": 1,
        "v_acc": -1,
        "h_acc": -1
    }""" % date_string
    print(payload)
    ws.send(payload)

websocket.enableTrace(True)
ws = websocket.WebSocketApp(WS_URL,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
rel.signal(2, rel.abort)  # Keyboard Interrupt
rel.dispatch()


# wscat -c "wss://xprize.mydronefleets.com/live/tracker/netrid/?drone_id=1b058a6e5d66031f11f71684b302f51d&access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNpZy1ycy0wIn0.eyJwbGV4Ijp7ImNvbXBhbnlfaWQiOiIxYjA1OGE2ZTVkNjYwMzFmMTFmNzE2ODRiMzAxYTU1YiIsImNsaWVudF9pZCI6IjFiMDU4YTZlNWQ2NjAzMWYxMWY3MTY4NGIzMDFhNTViIn0sImp0aSI6IlVTcHJ3akdzelpqQXdGdnpOWWEyWiIsImlhdCI6MTY4MDY4OTI5MiwiZXhwIjoxNjg4NDY1MjkyLCJpc3MiOiJodHRwczovL2lkZW50aXR5LmdhcnVkYS5pbyIsImF1ZCI6IjFiMDU4YTZlNWQ2NjAzMWYxMWY3MTY4NGIzMDFhNTViIn0.LmgpjNFmojJMMaHu_JT42owVPY9cGBhx8wbxwq88cK_sHUapiYYGJNu5kyJNRWwFOQOi30MlJ7mbeWH1PKLu3_H5SvUpKQtyn8GB7jUabqnLaHLa5Sl76KBhRyP_Zy5YDSu8AqD8HAVh4ON8si-goGmZQXVXmejN12islJvGMdc4DqhKGmQ90T0sVpum51IQAqchKFEtLfhZgQuGsdfQWbyhLTEVQk_DY4pMeRQGfNqA20-IBxbETwccT42zYXYG4XDnUY-UtaFA3BJ9AquXJphc97kTpdPV4uPhosXeoncVTJgWd9CZzg5uPNfPM2yQKoYdb4ZxTZN0qHnSMTMHeA"

# { "t": "2023-04-24T03:12:37.604409Z", "lat": "", "lng": "", "alt": 0, "status": 1, "v_acc": -1, "h_acc": -1 }


