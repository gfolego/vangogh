# Automatically Identifying Van Gogh's Paintings

This is the source code used in the paper
"From Impressionism to Expressionism: Automatically
Identifying Van Gogh's Paintings", which has been
published on the 23rd IEEE International Conference
on Image Processing (ICIP 2016).

The paper is available at IEEE Xplore:
[https://dx.doi.org/10.1109/icip.2016.7532335](https://dx.doi.org/10.1109/icip.2016.7532335)

The dataset is available at figshare:
[https://dx.doi.org/10.6084/m9.figshare.3370627](https://dx.doi.org/10.6084/m9.figshare.3370627)

Corresponding author:
Anderson Rocha ([anderson.rocha@ic.unicamp.br](mailto:anderson.rocha@ic.unicamp.br))


If you find this work useful in your research, please cite the paper!  :-)

```
@InProceedings{folego2016vangogh,
    author = {Guilherme Folego and Otavio Gomes and Anderson Rocha},
    booktitle = {2016 IEEE International Conference on Image Processing (ICIP)},
    title = {From Impressionism to Expressionism: Automatically Identifying Van Gogh's Paintings},
    year = {2016},
    month = {Sept},
    pages = {141--145},
    keywords = {Art;Feature extraction;Painting;Support vector machines;Testing;Training;Visualization;CNN-based authorship attribution;Painter attribution;Data-driven painting characterization},
    doi = {10.1109/icip.2016.7532335}
}
```


---

## Quick Guide

This guide has four sections:

1. *Creating the dataset* - Create your own dataset, or (even better!) expand on **VGDB-2016**.
2. *Using our method* - Use our method, given a dataset.
3. *Predicting debated paintings* - Predict debated paintings with our method.
4. *Calculating scores* - Transform distances into probabilities.


General note: all the scripts presented here have a `--help` argument,
which describes the script and possible parameters.


## Creating the dataset

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
identify -format "%f:%Q\n" res/img/orig/* | grep -v ^$ | sort -k2nr -k1 -t:
```


Resize images to the standard density.
```bash
python src/crawler/resize_images.py --csv res/db/db.csv --original res/img/orig/ --resized res/img/resz/
```


## Using our method

Requirements

- Caffe
- Parallel
- Python, and the following packages:
    - scikit-image
    - scikit-learn
- Unzip


From now on, we will assume that the **vgdb_2016.zip** dataset file has already been downloaded.

Unzip the dataset.
```bash
unzip vgdb_2016.zip
```

Create a directory for resources.
```bash
mkdir -pv vgdb_2016/{train,test}/{patch,feats}
```

Extract patches from each image.
```bash
find vgdb_2016/train/{,n}vg -type f | parallel python src/analysis/patch_extraction.py --image {} --dir vgdb_2016/train/patch/
find vgdb_2016/test/{,n}vg -type f | parallel python src/analysis/patch_extraction.py --image {} --dir vgdb_2016/test/patch/
```

Extract features from each patch.
In our work, we used the *VGG 19-layer model*, which is available at [http://www.robots.ox.ac.uk/~vgg/research/very_deep/](http://www.robots.ox.ac.uk/~vgg/research/very_deep/).
```bash
ls vgdb_2016/train/patch/ > vgdb_2016/train/patch_list.txt
ls vgdb_2016/test/patch/ > vgdb_2016/test/patch_list.txt

python src/analysis/caffe_extract_features.py --proto path/to/VGG_ILSVRC_19_layers_deploy.prototxt --model path/to/VGG_ILSVRC_19_layers.caffemodel --list vgdb_2016/train/patch_list.txt --input vgdb_2016/train/patch/ --output vgdb_2016/train/feats/
python src/analysis/caffe_extract_features.py --proto path/to/VGG_ILSVRC_19_layers_deploy.prototxt --model path/to/VGG_ILSVRC_19_layers.caffemodel --list vgdb_2016/test/patch_list.txt --input vgdb_2016/test/patch/ --output vgdb_2016/test/feats/
```

Create a directory for the classification model.
```bash
mkdir -pv vgdb_2016/clf
```

Generate classification model.
```bash
python src/analysis/generate_model.py --dir vgdb_2016/train/feats/ --model vgdb_2016/clf/model.pkl
```

Classify paintings in the test set using the Far method.
```bash
python src/analysis/classify.py --dir vgdb_2016/test/feats/ --model vgdb_2016/clf/model.pkl --aggregation far --gtruth
```

Done!


## Predicting debated paintings

Create a directory for resources.
```bash
mkdir -pv vgdb_2016/check/{patch,feats}
```

Extract patches from each image.
```bash
find vgdb_2016/check/[0-9]*.png -type f | parallel python src/analysis/patch_extraction.py --image {} --dir vgdb_2016/check/patch/
```

Extract features from each patch.
```bash
ls vgdb_2016/check/patch/ > vgdb_2016/check/patch_list.txt
python src/analysis/caffe_extract_features.py --proto path/to/VGG_ILSVRC_19_layers_deploy.prototxt --model path/to/VGG_ILSVRC_19_layers.caffemodel --list vgdb_2016/check/patch_list.txt --input vgdb_2016/check/patch/ --output vgdb_2016/check/feats/
```

Classify paintings using the Far method.
```bash
python src/analysis/classify.py --dir vgdb_2016/check/feats/ --model vgdb_2016/clf/model.pkl --aggregation far
```

In the output, class 1 means *van Gogh*, and class 0 means *non-van Gogh*.


## Calculating scores

Generate scores  model.
```bash
python src/analysis/generate_score/model.py --dir vgdb_2016/train/feats/ --model vgdb_2016/clf/model.pkl --score vgdb_2016/clf/score.pkl
```

