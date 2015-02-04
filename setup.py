from setuptools import setup, find_packages
setup(
    name="greenev",
    version="0.1.3",
    description="greenev is a Python networking service framework that bseed on greenlet's coroutine, it is event driven and use non-blocking socket model. It makes writing synchronous code gain the advantage of asynchronous execution.",
    author="Hevienz",
    url="https://github.com/Hevienz/greenev",
    license="Apache License Version 2.0",
    packages= find_packages(),
)
