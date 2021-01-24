import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PythonSafeEval", # Replace with your own username
    version="0.0.1",
    author="Allen Chou",
    author_email="s3131212@gmail.com",
    description="Safely execute arbitrary Python codes using nsjail.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/s3131212/PythonSafeEval",
    packages=['PythonSafeEval'],
    package_data={'PythonSafeEval': ['*.txt']},
    license="MIT License",
    python_requires='>=3.6',
)