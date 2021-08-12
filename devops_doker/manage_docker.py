import docker
from .errors import *
import socket

def check_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(('127.0.0.1', port))
    s.close()
    return result == 0
        

# config the docker environment
CLIENT = docker.from_env()


def showNotRunning():
    for i in CLIENT.containers.list(filters={'status': "exited"}):
        print('Container Id:' + i.id,
              'Container Name:' + i.name)


def showRunning():
    for i in CLIENT.containers.list(filters={'status': "running"}):
        print('Container Id:' + i.id,
              'Container Name:' + i.name)


def showAll():
    return list(CLIENT.containers.list(all=True))


def createContainer(imageName, name, command="", port={}):
    for i in port.values():
        if int(i) not in list(range(20000, 30000)):
            raise PortOutOfRange
        if check_port(int(i)):
            raise PortInUse
    if CLIENT.containers.list(filters={'name': name}):
        raise NameInUse
    if CLIENT.containers.list(filters={'name': name}):
        pass
    if command == "" and port == {}:
        CLIENT.containers.run(imageName, detach=True, name=name)
    elif port == {}:
        CLIENT.containers.run(imageName, command, detach=True, name=name)
    else:
        CLIENT.containers.run(imageName, command, detach=True, ports=port, name=name)


def startContainer(id):
    container = CLIENT.containers.get(id)
    container.start()


def stopContainer(id):
    container = CLIENT.containers.get(id)
    container.stop()

# stopContainer('192240ad75a8fb1bf30705a5fcc45911c63d2f94a6c8fd337fe74686212b69d1')


def deleteContainer(id, force=False):
    container = CLIENT.containers.get(id)
    try:
        container.remove(force=force)
    except docker.errors.APIError:
        raise DeleteError('Cannot Remove a running container, Stop it before or Use the force.')

# deleteContainer('4f49260ef821')


def runCommand(id, command):
    container = CLIENT.containers.get(id)
    print(container.exec_run(command, tty=True))
# runCommand('906c0904eff504b25800863fc95a4dccddd6b7c966e8c6802f71454eede9d2aa', 'echo Hello')


def deleteImage(name, force=False):
    try:
        CLIENT.images.remove(name, force=force)
    except docker.errors.APIError:
        raise DeleteError('Cannot remove, container is using the image, remove the container or use the force')
# deleteImage('alpine')


def createImage(full_path, tag):
    try:
        image = CLIENT.images.build(path=full_path, tag=tag)
        print(image[0].id)
    except docker.errors.BuildError:
        raise BuildFailed('There was an error during the build, check logs and Dockerfile')


if __name__ == '__main__':
    path = '.'
    print(path)
    createImage(path, 'testimage')
