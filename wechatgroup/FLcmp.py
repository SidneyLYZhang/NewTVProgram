import filecmp
import os

patho = 'C:/Users/alfch/Desktop/Images/'
patht = 'C:/Users/alfch/Desktop/Images - 副本/'

cf = open("C:/Users/alfch/Desktop/name.txt","w")

for root, dirs, files in os.walk(patho):
    for pic in files:
        for ro,di,fi in os.walk(patht):
            for pi in fi:
                if(os.path.exists(patho+pic)):
                    if(filecmp.cmp(patho+pic, patht+pi)):
                        cf.write(pic + "," + pi + "\n")

cf.close()