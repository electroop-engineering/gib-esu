from setuptools import find_packages, setup

setup(
    name="gib-esu",
    version="1.0.0",
    description="GİB EŞÜ EKS servis istemcisi - Electroop",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Electroop Engineering",
    author_email="dev@electroop.io",
    url="https://github.com/electroop-engineering/gib-esu",
    packages=find_packages(),  # Automatically finds package directories
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas==2.2.2",
        "pydantic==2.9.2",
        "python-dotenv==1.0.0",
        "requests==2.32.3",
    ],
)
