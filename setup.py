import io
import re

from setuptools import setup, find_packages

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("hon_xml/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = [\'"](.*?)[\'"]', f.read(), re.M).group(1)

setup(
    name="hon_xml",
    version=version,
    url="https://github.com/swquinn/hon-plugin-xml-renderer",
    project_urls={
        "Documentation": "https://swquinn.github.io/hon-plugin-xml-renderer",
        "Code": "https://github.com/swquinn/hon-plugin-xml-renderer",
        "Issue tracker": "https://github.com/swquinn/hon-plugin-xml-renderer/issues",
    },
    license="MIT",
    author="Sean Quinn",
    maintainer="swquinn",
    description="",
    long_description=readme,
    packages=find_packages(exclude='tests/*'),
    include_package_data=True,
    python_requires='>=3.0,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    install_requires=[
        'hon',
        'lxml'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'hon.renderers': [
            'xml_renderer=hon_xml:XmlRenderer'
        ]
    }
)
