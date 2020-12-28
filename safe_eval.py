import subprocess
from pathlib import Path
import shutil
import sys
import os
import random
import string

class SafeEval:
    def __init__(self, version=None, modules=None):
        self.__module_path = Path(__file__).parent
        self.__session_id = "python_safe_eval_" + self.__random_word()
        self.__session_path = self.__module_path / Path('.jailfs') / Path(self.__session_id)
        
        # check permission
        if not subprocess.check_output(["git", "--version"]).decode('utf-8').startswith("git version"):
            raise("Not Git installed or have no permission to access.")
        if not subprocess.check_output(["docker", "ps"]).decode('utf-8').startswith("CONTAINER ID"):
            raise("Not Docker installed or have no permission to access.")
        
        # fetch nsjail
        if not Path(self.__module_path / ".nsjail").is_dir():
            os.mkdir(self.__module_path / ".nsjail")
            subprocess.run("git clone https://github.com/google/nsjail.git .nsjail".split(), stdout=subprocess.DEVNULL)

        # create .jailfs
        if not (self.__module_path / ".jailfs").is_dir():
            os.mkdir(self.__module_path / ".jailfs")
        
        # create session path
        if not self.__session_path.is_dir():
            os.mkdir(self.__session_path)
        
        # copy nsjail
        shutil.copytree(self.__module_path / ".nsjail", self.__session_path / ".nsjail")

        # create Dockerfile
        with open(self.__module_path / "Dockerfile_template.txt", "r") as f:
            Dockerfile = f.read()
        
        Dockerfile = Dockerfile.format(
            version=version if version is not None else 3, 
            modules="RUN pip3 install " + " ".join(modules) if modules is not None else ""
        )

        with open(self.__session_path / "Dockerfile", "w+") as f:
            f.write(Dockerfile)

        # build docker image
        tempdir = os.getcwd()
        os.chdir(self.__session_path)
        subprocess.run("docker build --network=host -t {session_id}_image .".format(session_id=self.__session_id).split(), check=True, stdout=subprocess.DEVNULL)

        # run docker image
        subprocess.run("docker run --privileged --name={session_id} -v {session_path}:/volume -d -it {session_id}_image".format(session_id=self.__session_id, session_path=self.__session_path).split(), check=True, stdout=subprocess.DEVNULL)

    def __del__(self):
        # stop and remove docker container
        subprocess.run("docker stop {session_id}".format(session_id=self.__session_id).split(), check=True, stdout=subprocess.DEVNULL)
        subprocess.run("docker rm {session_id}".format(session_id=self.__session_id).split(), check=True, stdout=subprocess.DEVNULL)

        # remove image 
        subprocess.run("docker image remove {session_id}_image --no-prune".format(session_id=self.__session_id).split(), check=True, stdout=subprocess.DEVNULL)

        # remove session directory
        shutil.rmtree(self.__session_path)

    def eval(self, code=None, time_limit=0):
        if code is None:
            return
        
        # save file to the volume
        volume_filename = self.__random_word() + ".py"
        with open(self.__session_path / volume_filename, "w+") as f:
            f.write(code)
        
        # execute code
        return self.__execute_file_in_volume(volume_filename, time_limit)

    def execute_file(self, filename=None, time_limit=0):
        if filename is None:
            return
        
        # save file to the volume
        volume_filename = self.__random_word() + ".py"
        shutil.copyfile(Path(__file__).parent /  filename, self.__session_path / volume_filename)

        # execute code
        return self.__execute_file_in_volume(volume_filename, time_limit)
        
    def __execute_file_in_volume(self, volume_filename, time_limit):
        command = "docker exec {session_id} nsjail --user 99999 --group 99999 --disable_proc --chroot / --really_quiet --time_limit {time_limit} /usr/bin/python3 /volume/{volume_filename}".format(session_id=self.__session_id, time_limit=time_limit, volume_filename=volume_filename)
        return subprocess.run(command.split(" "), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def __random_word(self, length=12):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))