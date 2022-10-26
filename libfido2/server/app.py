import os 
from flask import Flask ,request, redirect, url_for
from flask import render_template, send_file
from os.path import isdir, join
import subprocess
from subprocess import PIPE

app = Flask(__name__)
mypath = "/home/ytlin/Desktop/working/libfido/test/server/user"


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/register_request", methods=['post'])
def register_request():
    global register_pending 
    register_pending = 0
    global last_register_user 
    last_register_user = ""
    username = request.form.get('Username')
    folders = os.listdir('./user')
    for f in folders:
        fullpath = join(mypath, f)
        if isdir(fullpath) and f == username:
            print(f)
            return "User exists\n"
    folder_path = "user/"+username
    print("create folder: ", folder_path)
    comp_process = subprocess.run(["mkdir", folder_path], stdout=PIPE, stderr=PIPE)
    file_path = folder_path + "/cred_param"
    exec_code = "bash cred.sh " + username
    os.system(exec_code)
    #print(comp_process.stdout)

    register_pending = 1
    last_register_user = username
    return send_file(file_path)

@app.route("/register_confirm", methods=['post']) # need a request pending
def register_confirm():
    global register_pending 
    global last_register_user 
    
    if register_pending == 0 or last_register_user == "":
        return "Something wrong..."
    
    cred = request.form.get('Username')
    
    return "Register Successfully"


@app.route("/login_request", methods=['post'])
def login_request():
    username = request.form.get('Username')
    folders = os.listdir('./user')
    folder_path = "user/"+username
    for f in folders:
        fullpath = join(mypath, f)
        if isdir(fullpath) and f == username:
            file_path = folder_path + "/assert_param"
            exec_code = "bash assert.sh " + username
            os.system(exec_code)
            return send_file(file_path)
    
    return "User not exists"


@app.route("/login_confirm") # need another request pending
def login_confirm():
    return "4"

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', ssl_context='adhoc', debug=True)