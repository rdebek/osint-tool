from setuptools import setup, find_packages

setup(
    name='osint_tool',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'pwn_check = osint_tool.main:pwn_check',
            'site_report = osint_tool.main:site_report',
        ],
    },
)