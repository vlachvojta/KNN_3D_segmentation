# KNN_3D_segmentation
KNN project (Convolutional Neural Networks) at FIT (B|V)UT. 2023/2024 summer semestr.

## Zadání

Libovolnou segmentační úlohu lze změnit na interaktivní tím, že na vstup sítě nedám jen obraz, ale i uživatelský vstup, třeba jako další "barevný" kanál s místy, které uživatel označil. Podobně to jde u bodových mrače. Můžete využít existující datasety (např. [KITTI](http://www.cvlibs.net/datasets/kitti/eval_semantics.php), [NYU Depth V2](https://cs.nyu.edu/~silberman/datasets/nyu_depth_v2.html), [NYU Depth V2 - Kaggle](https://www.kaggle.com/datasets/soumikrakshit/nyu-depth-v2)), nebo si i můžete pujčit LIDAR Livox Horizon, přípdaně nějakou RGB-D kameru typu Kinect.
Ning Xu, Brian Price, Scott Cohen, Jimei Yang, and Thomas Huang. Deep Interactive Object Selection. CVPR 2016. https://sites.google.com/view/deepselection


## TODOs
- [x] vybrat dataset - zatím S3DIS
- [ ] vybrat prostředí experimentu (pyTorch, open3DML, kombinace)
- [ ] Zkusit různé architektury (grafové sítě, PointNet++ spešl síť)
- [ ] vytvořit neinteraktivní baseline

## Datasety

- S3DIS - [paperswithcode.com/dataset/s3dis](https://paperswithcode.com/dataset/s3dis)
  - měl by to být pointCloud dataset (normály, barvy...), TODO stažení přes Google Formulář...
- NUY - RGBD
- KITTI - point cloudy
- Předzpracování / augmentace: zkusit různý rotace, skew, shift… (viz PointNet článek)
- Augmentace: jak zadávat náhodně negativní vstupy okolo…
- Na vstup dát i normály (z RGB-D do point cloudu to musíme dopočítat/doodhadnout třeba pomocí open3D)


## Rámcový postup

1) Baseline:
    - Neinteraktivní segmentace na point cloudech
2) Interactive rozšíření
    - Trénování pomocí samplování jedné třídy z původního datasetu
    - Jenom pozitivní body
3) Rozšíření o negativní body
    - Přidat negativní body do trénovací sady
4) Přidat možnost víc bodů
    - Input je už částečně obarvenej point cloud + nový bod pozitivní / negativní

## Architektura modelu
- Grafové neuronové sítě
- Existují i speciální sítě na pointCloudy viz PointNet, PointNet++
- Popř. Transformery

## Prostředí experimentů
- Open3D-ML
- PyTorch
- [MinkowskiEngine](https://github.com/NVIDIA/MinkowskiEngine) - support přímo na point cloudy…

## Zdroje
Článek, co budeme prezentovat: [Interactive Object Segmentation in 3D Point Clouds, článek](https://arxiv.org/pdf/2204.07183.pdf)
3D Deep Learning Python Tutorial: PointNet Data Preparation: [https://freedium.cfd/https://towardsdatascience.com/3d-deep-learning-python-tutorial-pointnet-data-preparation-90398f880c9f](https://freedium.cfd/https://towardsdatascience.com/3d-deep-learning-python-tutorial-pointnet-data-preparation-90398f880c9f)
Srovnání různých způsobů data augmentation: [data augmentation](https://arxiv.org/ftp/arxiv/papers/2308/2308.12113.pdf)
