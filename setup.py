from distutils.core import setup

setup(
    name='tinyws',
    version='0.5',
    description='A tiny package for making websocket server.',
    author='Arty',
    author_email='artythedev@gmail.com',
    url='https://github.com/ArtyTheDev/tinyws',
    packages=[
        "tinyws",
        "tinyws.client"
    ],
    install_requires=[
        "starlette", "asgiref", "https://github.com/ArtyTheDev/tinyasgi.git"
    ],
    python_requires=">=3.6",
    platforms="any",
)
