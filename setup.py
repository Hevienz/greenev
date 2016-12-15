from setuptools import setup, find_packages

setup(
    name = 'greenev',
    version = '1.0.1',
    packages = find_packages(),
    url = 'https://github.com/Hevienz/greenev',
    license = 'Apache License Version 2.0',
    author = 'Hevienz',
    author_email = 'hevienz@qq.com',
    description = "greenev is a Python networking service framework that bseed on coroutine realized by greenlet, "
                  "it is event driven and use non-blocking socket model. "
                  "It makes writing synchronous code gain the advantage of asynchronous execution.",
    install_requires = [
        "greenlet>=0.4.10",
    ],
    zip_saft = True,
)
