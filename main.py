from flask import Flask, render_template, redirect, request, jsonify
import pprint
import pymongo
import os
import devops_doker
import threading
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/home/yotamk/devops_flask/Dockerfiles"
client = pymongo.MongoClient(
    "mongodb+srv://admin:admin@cluster0.hpip7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
)
DB = client['kube']
CONTAINERS = DB['containers']


@app.route('/UploadDockerfile', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        image_name = request.form['Image']
        error = ""
        if 'file' not in request.files:
            print(1)
            return redirect("/NewImage?error=NoFile")
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return redirect("/NewImage?error=NoFile")
        if file:
            filename = file.filename
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Dockerfile')
            file.save(full_path)
            try:
                devops_doker.manage_docker.createImage(app.config['UPLOAD_FOLDER'], image_name)
            except devops_doker.errors.BuildFailed:
                return redirect("/NewImage?error=BuildFailed")
            return redirect("/NewImage?error=None")
    return redirect("/NewImage?error=unknown")


@app.route('/')
def index():
    dockers = CONTAINERS.find({})
    return render_template('index.html', dockers=dockers)


@app.route('/NewDocker')
def NewDocker():
    if request.args.get("error") == "NameInUse":
        error = "The Name is already in use"
    elif request.args.get("error") == "PortOutOfRange":
        error = "The port is out of range (20,000 - 30,000)"
    elif request.args.get("error") == "PortInUse":
        error = "The port is already in use"
    elif request.args.get("error") == "UnkownError":
        error = "An unknown error has occured. contact your administrator"
    else:
        error = None
    return render_template('NewDocker.html', error=error)


@app.route('/NewImage')
def NewImage():
    if request.args.get("error") == 'NoFile':
        error = "The file upload failed, no file selected"
    elif request.args.get("error") == 'unknown':
        error = "The file upload failed, unknown error"
    elif request.args.get("error") == "BuildFailed":
        error = "The build faild due to an unknown error"
    else:
        error = None
    return render_template('NewImage.html', error=error)


@app.route('/CreateContainer', methods=["POST"])
def CreateDocker():
    name = request.form["Name"].strip()
    image = request.form["Image"].strip()
    port = request.form["Port"]
    command = request.form["Command"]
    error = ""
    if port:
        ports = port.split(',')
        port = {}
        for i in ports:
            i = i.strip().split(":")
            port[i[0]] = i[1]
    print(image, name, port, command)
    try:
        if port and command:
            devops_doker.manage_docker.createContainer(image, name, port=port, command=command)
        elif port:
            devops_doker.manage_docker.createContainer(image, name, port=port)
        elif command:
            devops_doker.manage_docker.createContainer(image, name, command=command)
        else:
            devops_doker.manage_docker.createContainer(image, name)
        CONTAINERS.insert_one(
            {
                "id": None,
                "name": name,
                "image": image,
                "status": None
            }
        )
    except devops_doker.errors.PortOutOfRange:
        error = "PortOutOfRange"
    except devops_doker.errors.NameInUse:
        error = "NameInUse"
    except devops_doker.errors.PortInUse:
        error = "PortInUse"
    except devops_doker.errors.UnkownError:
        error = "UnkownError"

    if error:
        return redirect(f"/NewDocker?error={error}")
    updateDB()
    return redirect("/")


@app.route("/DeleteDocker")
def DeleteDocker():
    docker_id = request.args.get("docker")
    try:
        devops_doker.manage_docker.deleteContainer(docker_id)
        CONTAINERS.delete_one({"id": docker_id})
        error = ""
    except devops_doker.errors.DeleteError:
        error = 'Cannot Remove a running container, Stop it before or Use the force.'
    return error


@app.route("/StartDocker")
def StartDocker():
    try:
        docker_id = request.args.get("docker")
        devops_doker.manage_docker.startContainer(docker_id)
        updateDB()
        error = ""
    except Exception as e:
        error = e
    return error


@app.route("/StopDocker")
def StopDocker():
    docker_id = request.args.get("docker")
    try:
        devops_doker.manage_docker.stopContainer(docker_id)
        updateDB()
        error = ""
    except Exception as e:
        error = e
    return error


def monitor():
    while True:
        time.sleep(5)
        try:
            updateDB()
        except Exception as e:
            print(e)


def updateDB():
    for docker in devops_doker.manage_docker.showAll():
        if list(CONTAINERS.find({"name": docker.name})):
            CONTAINERS.update_one(
                {"name": docker.name},
                {
                    "$set": {
                        "id": docker.id,
                        "status": docker.status
                    }
                }
            )

if __name__ == '__main__':
    threading.Thread(target=monitor).start()
    app.run(host='0.0.0.0', port=80, debug=True)

