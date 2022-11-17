
#
#  class is used to generate random images using a part img, mask, and lot of background images


class PartImgDataSetGenerator:
    def __init__(self, partImg, bgImgDirPath, randomLoc = True, 
            randomRotation= True, mirroring=False, nImgsToGenerate =300):
        self.partImg = partImg
        self.bgImgDirPath = bgImgDirPath
        self.randomLoc = randomLoc
        self.randomRotation = randomRotation
        self.mirroring = mirroring
        self.nImgsToGenerate = nImgsToGenerate

    def __str__(self) -> str:
        return "class is used to generate random images using a part img, mask, and lot of background images"


    