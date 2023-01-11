from distutils.core import setup

setup(
    name='tinyws',
    version='0.4',
    description='A tiny package for making websocket server.',
    author='Arty',
    author_email='artythedev@gmail.com',
    url='https://github.com/ArtyTheDev/tinyws',
    packages=[
        "tinyws.client",
        "tinyws.server",
        "tinyws.server.interface"
    ],
    python_requires=">=3.6",
    platforms="any",
)
