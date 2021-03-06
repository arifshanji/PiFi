from flask import Flask, request, jsonify, json
import subprocess

app = Flask(__name__)

# Server

@app.route("/verify")
def verify():
    return jsonify(pifi=True)

@app.route("/wifi", methods = ['GET', 'POST'])
def wifi():
    if request.method == 'GET':
        return parseSSID()
    if request.method == 'POST':
        ssid = request.form['ssid']
        password = request.form.get('password', "")
        returnCode = AddNetwork(ssid, password)
        if returnCode == 0:
            return jsonify(success=True)
        else:
            return jsonify(success=False)

@app.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

# Helper Functions

def AddNetwork(ssid, password):
    returnCode = subprocess.call(['sudo',  '/usr/bin/addNetwork.sh', ssid, password])
    NetworkAdded()
    return returnCode

def NetworkAdded():
    process = subprocess.Popen("sudo systemctl restart autohotspot.service", shell=True)

def start_server():
    app.run(host='0.0.0.0')
    print("Server Started")

def parseSSID():
    returnCode = subprocess.call(["sudo iw dev wlan0 scan ap-force > /tmp/scanOutput"], shell=True)
    if returnCode != 0:
        return []
    else:
        inputFile = open("/tmp/scanOutput")
        networksDict = []
        ssid = ""
        protected = True

        for line in inputFile:
            line = line.strip()
            if "SSID:" in line:
                ssid = line[6:]
                if ssid != "":
                    newEntry = {'ssid': ssid,
                                'protected': protected
                                }
                    dupFlag = False
                    for entry in networksDict:
                        if entry['ssid'] == ssid:
                            dupFlag = True
                    if not dupFlag:
                        networksDict.append(newEntry)
            if "Encryption key:" in line:
                if line[15:] == "on":
                    protected = True
                else:
                    protected = False
        return jsonify(networks=networksDict)


# Main
if __name__ == '__main__':
    start_server()

