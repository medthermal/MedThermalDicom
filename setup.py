from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="thermal-dicom",
    version="1.0.0",
    author="Thermal DICOM Contributors",
    author_email="support@thermal-dicom.org",
    description="Professional thermal imaging DICOM library for medical applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thermal-dicom/thermal-dicom",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydicom>=2.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "opencv-python>=4.5.0",
        "scipy>=1.7.0",
        "pillow>=8.0.0",
        "plotly>=5.0.0",
        "dash>=2.0.0",
        "dash-bootstrap-components>=1.0.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "thermal-dicom-viewer=thermal_dicom.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "thermal_dicom": ["data/*.json", "templates/*.html"],
    },
)