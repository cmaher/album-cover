import cv
import sys
import Image, ImageDraw, ImageFont 
from maxrect import mrp
import random

ttffile = "HelveticaNeue.ttf" 

def makeAlbum(nameStr, imgStr, titleStr):
    random.seed()
    img, p1, p2 = loadImage(imgStr)
    name = getName(nameStr)
    title = getTitle(titleStr)
   
    img = opencv_pil(img)
    colorshift(img)
    drawFonts(img, name, title, p1, p2)
    img = pil_opencv(img)
    cv.ShowImage("output image", img)
    cv.WaitKey(10000)
    cv.SaveImage("out.jpg", img)

def opencv_pil(cimg):
    pimg = Image.fromstring("RGB", cv.GetSize(cimg), cimg.tostring())
    return pimg

def pil_opencv(pimg):
    cimg = cv.CreateImageHeader(pimg.size, cv.IPL_DEPTH_8U, 3)
    cv.SetData(cimg, pimg.tostring())
    return cimg

def loadImage(imgStr):
    img = cv.LoadImage(imgStr, cv.CV_LOAD_IMAGE_COLOR)
    grayimg = cv.LoadImage(imgStr, cv.CV_LOAD_IMAGE_GRAYSCALE)
   
    binimg = cv.CreateImage(cv.GetSize(grayimg), cv.IPL_DEPTH_8U, 1)
    cv.AdaptiveThreshold(grayimg, binimg, 255, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C, cv.CV_THRESH_BINARY_INV, 7, 10)

    fg = cv.CreateImage(cv.GetSize(grayimg), cv.IPL_DEPTH_8U, 1)
    cv.Dilate(binimg, fg, iterations=4)
    cv.Erode(fg, fg, iterations=9)
    
    ll, ur = findRect(cv.GetMat(fg))

    return img, ll, ur

def colorshift(img):
    ac = (0,0,0)
    shift = 128 
    pxarr = img.load()
    redshift = int(random.uniform(-shift, shift))
    greenshift = int(random.uniform(-shift, shift))
    blueshift = int(random.uniform(-shift, shift))
    
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            c = pxarr[x,y]
            c = c[0] + redshift, c[1] + greenshift, c[2] + blueshift
            pxarr[x,y] = c


def findRect(imgmat):
    imglist = []
    for col in range(imgmat.cols):
        imglist.append([])
        for row in range(imgmat.rows):
            imglist[col].append(imgmat[row, col])
    ll, ur = mrp(imglist)
    return ll, ur

def drawFonts(img, name, title, p1, p2):
    nfont, tfont = getFonts(name, title, 32)
    
    p1, ncolor = getTextData(img, name, p1, nfont)

    tw, th = nfont.getsize(title)
    p2 = p2[0], p1[1] + th
    p2, tcolor = getTextData(img, title, p2, tfont)
    shift = 40
    tcolor = tcolor[0] + shift, tcolor[1] + shift, tcolor[2] + shift 

    drawing = ImageDraw.Draw(img)
    drawing.text(p1, name, font=nfont, fill=ncolor)
    drawing.text(p2, title, font=tfont, fill=tcolor)

def getFonts(name, title, size):
    lfont = ImageFont.truetype(ttffile, int(size * .666666))
    sfont = ImageFont.truetype(ttffile, size)

    if len(name) > len(title):
        nfont, tfont = lfont, sfont
    else:
        nfont, tfont = sfont, lfont

    return nfont, tfont

def getTextData(img, text, pt, font):
    w, h = font.getsize(text) 
    width, height = img.size

    if pt[0] + w > width:
        pt = width - w, pt[1]
    if pt[1] + h > height:
        pt = pt[0], height - h

    ac = (0,0,0)
    pxarr = img.load()
    for x in range(pt[0], pt[0] + w):
        for y in range(pt[1], pt[1] + h):
            ac = ac[0] + pxarr[x,y][0], ac[1] + pxarr[x,y][1], ac[2] + pxarr[x,y][2]
    total = w * h
    ac = 255 - ac[0] / total, 255 - ac[1] / total, 255 - ac[2] / total

    return pt, ac


def getTitle(titleStr):
    return titleStr

def getName(nameStr):
    return nameStr

def main():
    cv.NamedWindow("output image", cv.CV_WINDOW_AUTOSIZE)
    makeAlbum(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()
