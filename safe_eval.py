import subprocess
from pathlib import Path
from shutil import copyfile
import sys
import os

def run(code=None, filename=None, modules=None, version=None, time_limit=0, input=b""):
    if code is not None and filename is not None:
        raise("Either code or filename should be provided, but not both.")
    
    if not subprocess.check_output(["git", "--version"]).decode('utf-8').startswith("git version"):
        raise("Not Git installed or have no permission to access.")
    if not subprocess.check_output(["docker", "ps"]).decode('utf-8').startswith("CONTAINER ID"):
        raise("Not Docker installed or have no permission to access.")
    if not Path(".jailfs").is_dir():
        os.mkdir(".jailfs")

    with open(os.path.dirname(__file__) + "/Dockerfile_template.txt", "r") as f:
        Dockerfile = f.read()
    
    if not Path(os.path.dirname(__file__) + "/.jailfs").is_dir():
        os.mkdir(os.path.dirname(__file__) + "/.jailfs")
    
    copy_code = ""
    cmd = ""
    if code is not None:
        with open(os.path.dirname(__file__) + "/.jailfs/run.py", "w+") as f:
            f.write(code)
    else:
        copyfile(filename, os.path.dirname(__file__) + "/.jailfs/run.py")
    copy_code = "COPY ./.jailfs /jailfs"
    cmd = "CMD python3 /jailfs/run.py"
    
    Dockerfile = Dockerfile.format(
        version=version if version is not None else 3, 
        modules="RUN pip3 install " + " ".join(modules) if modules is not None else "",
        copy_code=copy_code
    )

    with open(os.path.dirname(__file__) + "/Dockerfile", "w+") as f:
        f.write(Dockerfile)
    
    tempdir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    subprocess.run(["sh", os.path.dirname(__file__) + "/setup.sh"], check=True, stdout=subprocess.DEVNULL)
    os.chdir(tempdir)

    command = """docker run --privileged --rm -it nsjailcontainer nsjail --user 99999 --group 99999 --disable_proc --chroot / --really_quiet --time_limit {time_limit} /usr/bin/python3 /jailfs/run.py""".format(time_limit=time_limit)
    result = subprocess.run(command.split(" "), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result


if __name__ == "__main__":
    print(run(modules=["numpy"], version="3.8", code='print("Hello World")'))