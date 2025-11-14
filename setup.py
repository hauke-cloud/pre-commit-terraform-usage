#!/usr/bin/env python3
"""Setup configuration for terraform-usage-validator."""

from setuptools import setup

setup(
    name='terraform-usage-validator',
    version='1.0.0',
    description='Validate and auto-generate Terraform usage blocks in README.md',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Organization',
    author_email='your-email@example.com',
    url='https://github.com/hauke-cloud/pre-commit-terraform-usage',
    license='MIT',
    py_modules=['terraform_usage_gen'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'terraform-usage-gen=terraform_usage_gen:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Quality Assurance',
    ],
    keywords='terraform documentation pre-commit github-actions gitlab-ci',
)
