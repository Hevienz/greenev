from distutils.core import setup

setup(
    name='greenev',
    version='0.1.5',
    packages=['greenev', 'greenev.reactor'],
    url='https://github.com/Hevienz/greenev',
    license='Apache License Version 2.0',
    author='hevienz',
    author_email='hevienz@qq.com',
    description="greenev is a Python networking service framework that bseed on greenlet's coroutine, it is event driven and use non-blocking socket model. It makes writing synchronous code gain the advantage of asynchronous execution."
)
