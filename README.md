# Python Safe Eval
Safely execute arbitrary python code using [nsjail](https://github.com/google/nsjail).

tl;dr
```python
import PythonSafeEval
from pathlib import Path

try:
    sf = PythonSafeEval.SafeEval(version="3.8", modules=["numpy"])
    print(sf.eval(code='print("Hello World")').stdout)
    print(sf.execute_file(filename=Path(__file__).parent / "test_numpy.py").stdout)
except:
    print("error")
```

## Installation
Install via `pip`:  
```
pip install PythonSafeEval
```
Or clone this repo.  

## Requirements
Python >= 3.6. No additional package is needed.  

To create the sandbox, the Python process must have access to `docker` and `git`.  
Notice that [giving access to docker daemon grants privileges equivalent to the root user](https://docs.docker.com/engine/security/#docker-daemon-attack-surface), so be careful.  


## Usage
First, initialize the sandbox. The `version` and `modules` stand for, well, the version of Python and the modules to install. `tmp_dir` stands for the directory to write temporary files. The package would create a directory in the supplied path, and write the code to that directory. If `tmp_dir` is not supplied, a temporary directory would be created. In termination, the directory would be removed.
```python
sf = PythonSafeEval.SafeEval(version="3.8", modules=["numpy"], tmp_dir='~/tmp/')
```
Notice that, since all scripts to be executed is stored in `tmp_dir`, strict control of permission is recommended.  

Next, to run a script, we have to method: supply a string or a file.  
To supply a string, use `sf.eval`, which returns a [subprocess.CompletedProcess](https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess).
```python
r = sf.eval(code='print("Hello World")')
```
To supply a file, use `sf.execute_file`, which, again, returns a [subprocess.CompletedProcess](https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess).
```python
r = sf.execute_file(filename=Path(__file__).parent / "test_numpy.py")
```

To limit the execution time, use the `time_limit` parameter. The default value is `0`, i.e., no limit.
```python
r = sf.eval(code='print("Hello World")', time_limit=10)
```

## How it works
During initialization, we first write a `Dockerfile` specifying Python version and modules, create a Docker image, and create a Docker container. We also create a temporary directory and mount the directory in the container. Whenever a script is supplied, we copy the script to a shared directory and use `nsjail <some parameters> python3 <your script>` to run the script.  Why nsjail in Docker? Because [Docker container is not a VM or a sandbox](https://docs.docker.com/engine/security/#linux-kernel-capabilities). In the destructor, the container is stopped and removed, the image is removed, and the temporary directory is also removed.  

## Security Issues
There are some security issues that all users should keep in mind.
1. [Giving access to docker daemon grants privileges equivalent to the root user](https://docs.docker.com/engine/security/#docker-daemon-attack-surface), so it's a good idea to separate the PythonSafeEval and the main application and limit the access between the two.
2. The code would be stored in the temporary directory, and the attacker may modify the file before PythonSafeEval execute it. While generally in the sandbox no harm can be done, the attacker could still paralyze the machine through infinite loops or heavy calculations. Therefore, set the `time_limit` when possible.
3. PythonSafeEval uses [nsjail](https://github.com/google/nsjail), which should be safe, but there's no guarantee.

Finally, there's no guarantee that this package is safe. Read the license for more information.

## Use in Docker
If your Python application is running in a Docker container, given that Docker can't be run in a Docker container (actually [you can](https://github.com/jpetazzo/dind), but DON'T DO THAT PLEASE), we have to let the container access the docker daemon.  

```
docker run <something> -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker -v /.jailfs:/.jailfs
```

Note that the path of the temporary directory inside the container and outside the container should be the same, e.g., `/.jailfs:/.jailfs`.  

## License
MIT License.