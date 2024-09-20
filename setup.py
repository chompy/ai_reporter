from setuptools import find_packages, setup

setup(
    name='ai_reporter',
    packages=find_packages(include=['ai_reporter', 'ai_reporter.*']),
    version='0.0.1',
    description='Use AI to generate reports with various tools and the ability to chain reports together based on previous results.',
    author='Nathan Ogden',
    install_requires=['pyyaml', 'requests', 'openai', 'GitPython', 'selenium', 'pillow']
)