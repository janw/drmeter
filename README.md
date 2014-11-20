# DRmeter for Python

**work in progress**

## Synposis

Based on the reverse-engineered algorithm proposed by the Pleasurize Music Foundation. While this function's output is not permitted to be called an  official Dynamic Range (DR) value it does still comply with 99.9% of the results of one of the official DR meters.

## Requirements

In order to run the DRmeter, you need to have the following Python packages installed:

* Numpy
* PySoundFile
* CFFI

The function has been developed using Python 3.4 on a Mac. Supported audio file formats are given by the underlying `libsndfile` library.

## Usage

```python
./drmeter.py <file or path>
```

## License

Copyright (c) <2013> Jan Willhaus

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files  (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.