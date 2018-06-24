# Dynamic Range meter

Analyze audio files for their Dynamic Range (DR) as proposed by the [Pleasurize Music Foundation](http://www.dynamicrange.de).

The algorithm has been reverse-engineered using the available information and officially endorsed software to calcuate the DR value. The output of `drmeter.py` is probably within 99.9% accuracy towards the official DR tools.

This project is in no way affiliated with the Pleasurize Music Foundation or its Dynamic Range Project.

## Requirements

In order to run the DRmeter, you need to have the following Python packages installed. Use the included `Pipfile` to install the dependencies via [Pipenv](https://docs.pipenv.org) (`pipenv install`)

* Numpy (v0.14.5)
* PySoundFile (v0.10.2)

The function has been developed using Python 3.6 on a Mac. The supported audio file formats are given by PySoundFile's underlying [libsndfile](http://www.mega-nerd.com/libsndfile/) library.

## Usage

```python
./drmeter.py <file or path>
```

**Example output**

```

DR analysis results:
====================
/Volumes/media/music/Coldplay/Mylo Xyloto/01-01 - Mylo Xyloto.flac

     :   Chann  1  ::  Chann  2  ::
Peak :    -2.49 dB ::   -3.08 dB ::
RMS  :   -14.60 dB ::  -14.59 dB ::
DR   :     7.76    ::    7.27    ::
```

Which closely matches the [results within the Dymanic Range DB](http://dr.loudness-war.info/album/view/79484).

## License

This project is under MIT license, see `LICENSE` for details.
