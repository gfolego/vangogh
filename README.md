# vangogh


```bash
mkdir -pv res/{db,img/{orig,resz,patch}}

url='Category:Still_life_paintings_of_flowers_by_Vincent_van_Gogh,_Auvers_1890'

python src/crawler/crawl2csv.py --url "$url" --csv res/db/"$url"

Rscript src/crawler/tidy_dataset.R --density 95 --output res/db/db.csv res/db/"$url" res/db/"$url"

python src/crawler/download_images_from_csv.py --csv res/db/db.csv --directory res/img/orig/

python src/analysis/resize_images.py --csv res/db/db.csv --original res/img/orig/ --resized res/img/resz/

find res/img/resz/ -type f | parallel python src/analysis/patch_extraction.py --image {} --dir res/img/patch/
```

