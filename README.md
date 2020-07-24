# wrf-nalcms

Process NALCMS land use data for ingestion into WRF.

## Getting started

### Get the code

```
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -U https://github.com/cloudruninc/wrf-nalcms
```

### Download NALCMS data

1. Follow this [link](http://www.cec.org/north-american-environmental-atlas/land-cover-30m-2015-landsat-and-rapideye/).
2. Download the 30-m land cover from 2015.
3. Unzip `north_america_2015.zip`.
4. Unzip `NA_NALCMS_2015_LC_30m_LAEA_mmu5pix_.zip`.
