from setuptools import setup, find_packages

setup(
    name='django_restful_translator',
    version='0.1.4',
    author='Alex Ivanchyk',
    author_email='alexander.ivanchik@gmail.com',
    description='A Django application providing translation functionalities for Django Rest Framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AlexIvanchyk/django_restful_translator',
    packages=find_packages(),
    install_requires=[
        'Django>=3.2',
        'djangorestframework>=3.12',
        'polib>=1.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    license='MIT',
    python_requires='>=3.6',
    keywords='django rest-framework translation i18n',
)
