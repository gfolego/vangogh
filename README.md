# From Impressionism to Expressionism: Automatically Identifying Van Gogh's Paintings

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


---

## Quick Guide

General note: all the scripts presented here have a `--help` argument,
which describes the script and possible parameters.


### Creating the dataset

Requirements

- ImageMagick
- Python, and the following packages:
    - hurry.filesize
    - numpy
    - progressbar2
    - wikitools
- R, and the following packages:
    - argparse
    - data.table
    - dplyr


Create a directory for resources.
```bash
mkdir -pv res/{db,img/{orig,resz}}
```

Define the URL to be crawled. This is just an example. In our work, we crawled more than 200 different URLs.
```bash
url='Category:Still_life_paintings_of_flowers_by_Vincent_van_Gogh,_Auvers_1890'
```

Crawl URL and collect metadata.
```bash
python src/crawler/crawl2csv.py --url "$url" --csv res/db/"$url"
```

Parse and clean up collected metadata.
We set different values here just as a working example.
Also, at this point, it is possible to provide multiple files at once, even with duplicated entries (as shown).
```bash
Rscript src/crawler/tidy_dataset.R --density 95 --ratio 0.15 --output res/db/db.csv res/db/"$url" res/db/"$url"
```

Dataset done, and the CSV file is at `res/db/db.csv`.
Now, you may choose to continue with your newly created dataset, or with the original **vgdb_2016.csv**.


Download images.
```bash
python src/crawler/download_images_from_csv.py --csv res/db/db.csv --directory res/img/orig/
```
Note: images with less than 75% of JPEG quality were manually removed
(both images and respective entries in the CSV file).
It is possible to check the quality with ImageMagick.

```bash
identify -format "%f:%Q\n" res/img/orig/* | grep -v ^$ | sort -k2nr -t:
```


Resize images to the standard density.
```bash
python src/analysis/resize_images.py --csv res/db/db.csv --original res/img/orig/ --resized res/img/resz/
```

Note: the file naming standard according to author has been applied manually.


### Using our method

Requirements

- Caffe
- Parallel
- Python, and the following packages:
    - scikit-image


Create a directory for resources.
```bash
mkdir -pv res/{img/patch,feats}
```

Extract patches from each image.
```bash
find res/img/resz/ -type f | parallel python src/analysis/patch_extraction.py --image {} --dir res/img/patch/
```

Extract features from each patch.
In our work, we used the *VGG 19-layer model*, which is available at [http://www.robots.ox.ac.uk/~vgg/research/very_deep/](http://www.robots.ox.ac.uk/~vgg/research/very_deep/).
```bash
ls res/img/patch/ > res/img/patch_list.txt
python src/analysis/caffe_extract_features.py --proto path/to/VGG_ILSVRC_19_layers_deploy.prototxt --model path/to/VGG_ILSVRC_19_layers.caffemodel --list res/img/patch_list.txt --input res/img/patch/ --output res/feats/
```


*(to be continued ...)*

