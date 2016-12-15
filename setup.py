from distutils.core import setup

setup(
    name = 'greenev',
    version = '1.0.0',
    packages = ['greenev', 'greenev.reactor'],
    url = 'https://github.com/Hevienz/greenev',
    license = 'Apache License Version 2.0',
    author = 'Hevienz',
    author_email = 'hevienz@qq.com',
    description = "greenev is a Python networking service framework that bseed on coroutine realized by greenlet, it is event driven and use non-blocking socket model. It makes writing synchronous code gain the advantage of asynchronous execution."
)
