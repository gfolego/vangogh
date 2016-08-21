## From Impressionism to Expressionism: Automatically Identifying Van Gogh's Paintings

This is the source code used in the paper
"From Impressionism to Expressionism: Automatically
Identifying Van Gogh's Paintings", which will be
published on the 23rd IEEE International Conference
on Image Processing (ICIP 2016).

The dataset is available at figshare:
[https://dx.doi.org/10.6084/m9.figshare.3370627](https://dx.doi.org/10.6084/m9.figshare.3370627)

Corresponding author:
Anderson Rocha ([anderson.rocha@ic.unicamp.br](mailto:anderson.rocha@ic.unicamp.br))


If you find this work useful in your research, please cite!  :-)


#### Quick Guide

Pre-requisites

- ImageMagick

- Parallel

- Python, and the following packages:
    - hurry.filesize
    - numpy
    - progressbar2
    - scikit-image
    - wikitools

- R, and the following packages:
    - argparse
    - data.table
    - dplyr


Create a directory for resources.
```bash
mkdir -pv res/{db,img/{orig,resz,patch}}
```

Define the URL to be crawled. This is just an example. In our work, we crawled more than 200 different URLs.
```bash
url='Category:Still_life_paintings_of_flowers_by_Vincent_van_Gogh,_Auvers_1890'
```

Crawl URL and collect metadata.
```bash
python src/crawler/crawl2csv.py --url "$url" --csv res/db/"$url"
```

Parse and clean up collected metadata. The default value for minimum density is 196.3, but we set a different value here just as an example. Also, at this point, it is possible to provide multiple files at once, even with duplicated entries. 
```bash
Rscript src/crawler/tidy_dataset.R --density 95 --output res/db/db.csv res/db/"$url" res/db/"$url"
```

Download images.
```bash
python src/crawler/download_images_from_csv.py --csv res/db/db.csv --directory res/img/orig/
```

Resize images to the standard density.
```bash
python src/analysis/resize_images.py --csv res/db/db.csv --original res/img/orig/ --resized res/img/resz/
```

This step is optional. In our method, we extract patches from each image.
```bash
find res/img/resz/ -type f | parallel python src/analysis/patch_extraction.py --image {} --dir res/img/patch/
```


