import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cost-power-monitor",
    version="1.1.0",
    author="Julian Held",
    author_email="julian.held@rub.de",
    license='MIT',
    platforms=['any'],
    description="GUI for continuously monitoring dissipated power of a COST-Jet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mimurrayy/COST-power-monitor/",
    packages=setuptools.find_packages(),
    install_requires=[
          'numpy>=1.17.0', 'scipy>=1.0.0', 'pyqtgraph>=0.10.0', 'pyusb>=1.01', 'PyQt5>=5.9'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    entry_points = {'gui_scripts': ['cost-power-monitor = cost_power_monitor:main']}
)
