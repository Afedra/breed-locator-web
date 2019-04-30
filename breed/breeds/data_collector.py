import os
import re
import pandas
import pickle
import random
import numpy
import imutils
import progressbar
import matplotlib.pyplot as plt
import seaborn as sns
from cv2 import cv2
from mahotas.features import haralick
from multiprocessing import Pool
from sklearn.decomposition import PCA
from django.conf import settings


def get_image_data():
    TRAINING_DATA = os.path.join(settings.BASE_DIR, "processing_data", "data")
    PICKLE_MODELS = os.path.join(settings.BASE_DIR, "processing_data", "pk_models")
    BREEDS = sorted(os.listdir(TRAINING_DATA))
    REF_POINT = []
    FIELD = 'bodies'
    RESULT_DICT = {}
    RESULT_DICT['bodies'] = []
    RESULT_DICT['heads'] = []
    IMAGE = None

    ############################################################################################################
    # Create Breed Path Bodies Heads Column                                                                    #
    # Update Breed Path Column First                                                                           #
    # Creating pickle file                                                                                     #
    ############################################################################################################

    pAnimals = pandas.DataFrame(columns=['breed', 'path', 'bodies', 'heads'])
    for BREED in BREEDS:
        PICS = os.listdir(os.path.join(TRAINING_DATA, BREED))
        for PIC in PICS:
            if os.path.isfile(os.path.join(os.path.join(TRAINING_DATA, BREED) , PIC)):
                pAnimals = pAnimals.append({'breed':BREED, 'path':os.path.join(os.path.join(TRAINING_DATA, BREED) , PIC)}, ignore_index=True)

    pickle.dump(pAnimals, open(os.path.join(PICKLE_MODELS , 'pAnimals.pd.pk'), 'wb'))

    ############################################################################################################
    # Create Image Dialog then record mouse callback events
    ############################################################################################################

    def getBBs(event, x, y, flags, param):
        # takes BGR CV2 image as an input
        # displays image and waits for
        # bounding boxes to be clicked
        # around animals' bodies and faces
        # returns np array of bounding boxes    
        nonlocal REF_POINT, FIELD

        if event == cv2.EVENT_LBUTTONDOWN:
            REF_POINT = [(x, y)]
            print('mouse down', x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            REF_POINT.append((x,y))
            RESULT_DICT[FIELD].append(REF_POINT)
            print('mouse up', x, y)        
            # draw a rectangle around the region of interest
            cv2.rectangle(IMAGE, REF_POINT[0], REF_POINT[1], (0, 255, 0), 2)
            cv2.imshow("image", IMAGE)
            print(RESULT_DICT)

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", getBBs)

    ############################################################################################################
    # Sort Pics
    ############################################################################################################

    BREED_COUNT = 0
    IMAGE_COUNT = 0
    BREED = BREEDS[BREED_COUNT]
    print('BREED:', BREED)
    print(len(PICS), '# of pics')
    PICS = pAnimals[pAnimals['breed'] == BREED].path.tolist()

    def loadIm(breed, randPic=False):
        # loads image from dataset
        # checks to make sure image is 
        # not none (in case its html, etc)
        nonlocal IMAGE_COUNT, PICS
        if randPic:
            IMAGE_PATH = random.choice(PICS)
        else:
            IMAGE_PATH = PICS[IMAGE_COUNT]
            print('pic #', IMAGE_COUNT)

        IMAGE = cv2.imread(IMAGE_PATH)
        print('image:', IMAGE_PATH.split('/')[-1])
        return IMAGE, IMAGE.copy(), IMAGE_PATH

    def writeROIs(RESULT_DICT, IMAGE_PATH):
        idx = pAnimals[pAnimals.path == IMAGE_PATH].index[0]
        if RESULT_DICT['bodies'] != []:
            pAnimals.iloc[idx, 2] = RESULT_DICT['bodies']
        if RESULT_DICT['heads'] != []:
            pAnimals.iloc[idx, 3] = RESULT_DICT['heads']
        FIELD = 'bodies'
        RESULT_DICT = {}
        RESULT_DICT['bodies'] = []
        RESULT_DICT['heads'] = []
        return FIELD, RESULT_DICT

    def nextIm(randPic=False, dir='foreground', newBreed=False):
        # increments through to the next image
        # writes and resets ROIs
        nonlocal IMAGE_COUNT, PICS
        if randPic:
            IMAGE, CLONE, IMAGE_PATH = loadIm(BREED, randPic=True)
        else:
            print(dir)
            if dir=='foreground':
                IMAGE_COUNT += 1
                if IMAGE_COUNT >= len(PICS):
                    IMAGE_COUNT = 0 # loop back to beginning if at end
                IMAGE_PATH = PICS[IMAGE_COUNT]
                IMAGE = cv2.imread(IMAGE_PATH)
                while IMAGE.all() == None:
                    IMAGE_COUNT += 1
                    if IMAGE_COUNT >= len(PICS):
                        IMAGE_COUNT = 0 # loop back to beginning if at end
                    IMAGE_PATH = PICS[IMAGE_COUNT]
                    IMAGE = cv2.imread(IMAGE_PATH)
            elif dir=='background':
                IMAGE_COUNT -= 1
                if IMAGE_COUNT < 0:
                    IMAGE_COUNT = len(PICS) - 1 # go to last pic if at beginning
                IMAGE_PATH = PICS[IMAGE_COUNT]
                IMAGE = cv2.imread(IMAGE_PATH)
                while IMAGE.all() == None:
                    IMAGE_COUNT -= 1
                    if IMAGE_COUNT < 0:
                        IMAGE_COUNT = len(PICS) - 1 # go to last pic if at beginning
                    IMAGE_PATH = PICS[IMAGE_COUNT]
                    IMAGE = cv2.imread(IMAGE_PATH)
            if newBreed:
                imCnt = 0
            IMAGE, CLONE, IMAGE_PATH = loadIm(BREED)
        print('image data:', pAnimals[pAnimals.path == IMAGE_PATH])
        return IMAGE, CLONE, IMAGE_PATH

    IMAGE, CLONE, IMAGE_PATH = loadIm(BREED)
    cv2.imshow("image", IMAGE)

    while True:
        # display the image and wait for a keypress
        key = cv2.waitKey(1) & 0xFF
        
        # for debugging
        if key!=255:
            print(key)
        
        # # if the 'r' key is pressed, reset everything
        if key == ord('r'):
            print('reset')
            print('tracking bodies')
            FIELD = 'bodies'
            RESULT_DICT = {}
            RESULT_DICT['bodies'] = []
            RESULT_DICT['heads'] = []
            IMAGE = CLONE.copy()
            cv2.imshow("image", IMAGE)
        
        # # if the 'b' key is pressed, log position of animals' bodies
        if key == ord('b'):
            print('tracking bodies')
            FIELD = 'bodies'
        
        # # if the 'f' key is pressed, log position of animals' faces
        if key == ord('f') or key == ord('a'):
            print('tracking faces')
            FIELD = 'heads'
        
        # # if the 'n' key is pressed, go to random animal pic
        if key == ord('n'):
            FIELD, RESULT_DICT = writeROIs(RESULT_DICT, IMAGE_PATH)
            IMAGE, CLONE, IMAGE_PATH = nextIm(randPic=True)
            cv2.imshow("image", IMAGE)
        
        # # if fwd (right) arrow pressed go to next in order pic
        if key == 43:
            FIELD, RESULT_DICT = writeROIs(RESULT_DICT, IMAGE_PATH)
            IMAGE, CLONE, IMAGE_PATH = nextIm(dir='foreground')
            cv2.imshow("image", IMAGE)
        
        if key == 45:
            FIELD, RESULT_DICT = writeROIs(RESULT_DICT, IMAGE_PATH)
            IMAGE, CLONE, IMAGE_PATH = nextIm(dir='background')
            cv2.imshow("image", IMAGE)
        
        # # if the 'd' key is pressed, go to next breed
        # # and load next pic
        if key == ord('d'):
            pickle.dump(pAnimals, open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes.pd.pk'), 'wb'))
            FIELD, RESULT_DICT = writeROIs(RESULT_DICT, IMAGE_PATH)
            BREED_COUNT += 1
            if BREED_COUNT >= len(BREEDS):
                print('reached end of breeds')
                break
            BREED = BREEDS[BREED_COUNT]
            print('BREED:', BREED)
            print(len(PICS), '# of pics')
            PICS = pAnimals[pAnimals['breed'] == BREED].path.tolist()
            IMAGE, CLONE, IMAGE_PATH = nextIm(newBreed=True)
            cv2.imshow('image', IMAGE)
        
        # # if the 'q' key is pressed, break from the loop
        elif key == ord('q'):
            RESULT_DICT = writeROIs(RESULT_DICT, IMAGE_PATH)
            break

    pickle.dump(pAnimals, open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes.pd.pk'), 'wb'))

    ###########################################################################################################
    # removes bounding boxes from accidental clicks
    ###########################################################################################################

    bb = pickle.load(open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes.pd.pk'), 'rb'))
    bb.dropna(inplace=True)
    toDrop = []

    for i in range(bb.shape[0]):
        # check if any bounding boxes are small (accidental click)
        # remove them from the temp array and then rewrite the data
        # if it changed
        IMAGE_PATH = bb.iloc[i].path
        IMAGE = cv2.imread(IMAGE_PATH)
        h, w = IMAGE.shape[:2]
        BODIES = bb.iloc[i].bodies
        NEW_BODIES = BODIES.copy()
        CHANGED = False
        BODY_COUNT = 0
        for BODY in BODIES:
            y1 = min([BODY[0][1], BODY[1][1]])
            y2 = max([BODY[0][1], BODY[1][1]])
            x1 = min([BODY[0][0], BODY[1][0]])
            x2 = max([BODY[0][0], BODY[1][0]])
            bc = [[x1, y1], [x2, y2]]
            CHANGED_BC = False
            bbDiffs = sum(abs(numpy.array(BODY[0])-numpy.array(BODY[1])))
            if bbDiffs < 20:
                print('removing', BODY, 'from index', i)
                CHANGED = True
                NEW_BODIES.remove(BODY)
            else:
                # take care of case where box is outside of image
                # first check xs
                if bc[0][0] < 0:
                    bc[0][0] = 0
                    CHANGED_BC = True
                if bc[1][0] > w:
                    bc[1][0] = w
                    CHANGED_BC = True
                # then ys
                if bc[0][1] < 0:
                    bc[0][0] = 0
                    CHANGED_BC = True
                if bc[1][1] > h:
                    bc[1][1] = h
                    CHANGED_BC = True
            if CHANGED_BC:
                # print(NEW_BODIES)
                # print(BODY_COUNT)
                NEW_BODIES[BODY_COUNT] = bc
                print('changed:')
                print(BODY)
                print(bc)
            BODY_COUNT += 1
        bb.iloc[i].bodies = NEW_BODIES
        
        # do the same for the heads bounding boxes
        HEADS = bb.iloc[i].heads
        NEW_HEADS = HEADS.copy()
        CHANGED = False
        HEAD_COUNT = 0
        for HEAD in HEADS:
            y1 = min([HEAD[0][1], HEAD[1][1]])
            y2 = max([HEAD[0][1], HEAD[1][1]])
            x1 = min([HEAD[0][0], HEAD[1][0]])
            x2 = max([HEAD[0][0], HEAD[1][0]])
            bc = [[x1, y1], [x2, y2]]
            CHANGED_BC = False
            bbDiffs = sum(abs(numpy.array(HEAD[0])-numpy.array(HEAD[1])))
            if bbDiffs < 20:
                print('removing', HEAD, 'from index', i)
                CHANGED = True
                NEW_HEADS.remove(HEAD)
            else:
                # take care of case where box is outside of image
                # xs first
                if bc[0][0] < 0:
                    bc[0][0] = 0
                    CHANGED_BC = True
                if bc[1][0] > w:
                    bc[1][0] = w
                    CHANGED_BC = True
                # ys next
                if bc[0][1] < 0:
                    bc[0][0] = 0
                    CHANGED_BC = True
                if bc[1][1] > h:
                    bc[1][1] = h
                    CHANGED_BC = True
            if CHANGED_BC:
                NEW_HEADS[HEAD_COUNT] = bc
                CHANGED = True
            HEAD_COUNT += 1
        bb.iloc[i].heads = NEW_HEADS
        # drop row if both bodies and heads bounding boxes are empty
        if NEW_BODIES == [] and NEW_HEADS == []:
            toDrop.append(i)

    bb.drop(bb.index[toDrop], inplace=True)
    pickle.dump(bb, open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes-clean.pd.pk'), 'wb'), protocol=2)

    ########################################################################################################
    # uses OpenCV grabCut() to segment dog from background -- WARNING: this script takes hours to complete
    ########################################################################################################

    BLUE = [255,0,0]        # rectangle color
    RED = [0,0,255]         # PR BG
    GREEN = [0,255,0]       # PR FG
    BLACK = [0,0,0]         # sure BG
    WHITE = [255,255,255]   # sure FG

    DRAW_BG = {'color' : BLACK, 'val' : 0}
    DRAW_FG = {'color' : WHITE, 'val' : 1}
    DRAW_PR_FG = {'color' : GREEN, 'val' : 3}
    DRAW_PR_BG = {'color' : RED, 'val' : 2}

    bb = pickle.load(open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes-clean.pd.pk'), 'rb'))
    bb.dropna(inplace=True)

    startIm = 0 # got interrupted here...uncomment if you need to resume mid-dataframe
    widgets = ["grabCutting images: ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
    pbar = progressbar.ProgressBar(maxval=bb.shape[0]-startIm, widgets=widgets).start()

    def get_rect(rectI):
        # takes unsorted rectangle from pandas DF
        # returns rectangle for grabcut (x, y, dx, dy)
        rect = (min(bd[0][0], bd[1][0]), min(bd[0][1], bd[1][1]), abs(bd[1][0] - bd[0][0]), abs(bd[1][1] - bd[0][1]))
        return rect

    for i in range(startIm, bb.shape[0]):
        try:
            pbar.update(i)
        except:
            pass
        entry = bb.iloc[i]
        GRABCUT_DIR = os.path.join(TRAINING_DATA , entry.breed , 'grabcut')
        # make fg and bg directory if needed
        if not os.path.isdir(GRABCUT_DIR):
                os.makedirs(GRABCUT_DIR)
        for dd in ['foreground/', 'background/']:
            if not os.path.isdir(os.path.join(GRABCUT_DIR , dd)):
                os.makedirs(os.path.join(GRABCUT_DIR , dd))
        
        # get filename of image
        imName = entry.path.split('/')[-1]
        ext = re.search('\.\w', imName)
        print(imName) # for debugging

        if ext:
            imName = imName.split('.')[0]    
        elif imName[-1]=='.':
            imName = imName[:-1]
        
        print(imName) # for debugging

        try:
            image = cv2.imread(entry.path)
        except:
            continue

        orig = image.copy()
        bods = entry.bodies

        # only working now for single rectangle
        if len(bods) == 1:
            bd = bods[0]
            
            # do first iterations of grabcut
            bgdmodel = numpy.zeros((1,65),numpy.float64)
            fgdmodel = numpy.zeros((1,65),numpy.float64)
            rect = get_rect(bd)        
            mask = numpy.zeros(image.shape[:2], dtype = numpy.uint8) # mask initialized to BG
            cv2.grabCut(image, mask, rect, bgdmodel, fgdmodel, 5, cv2.GC_INIT_WITH_RECT)
            
            # second iterations of grabcut - sometimes it doesn't work
            try:
                cv2.grabCut(orig, mask, rect, bgdmodel, fgdmodel, 5, cv2.GC_INIT_WITH_MASK)
            except cv2.error as err:
                print(err)
            
            # make images with alpha channel
            b_channel, g_channel, r_channel = cv2.split(orig)
            # if probably background (2) or background (0), set to trasparent (0)
            # otherwise make opaque (255)
            a_channel = numpy.where((mask==2)|(mask==0), 0, 255).astype('uint8')
            foreground = cv2.merge((b_channel, g_channel, r_channel, a_channel))
            # same idea for background, just inverted
            a_channel_bg = numpy.where((mask==2)|(mask==0), 255, 0).astype('uint8')
            background = cv2.merge((b_channel, g_channel, r_channel, a_channel_bg))
            #cv2.imshow('fg', foreground) # for debugging
            #cv2.imshow('bg', background)
            cv2.imwrite(os.path.join(GRABCUT_DIR , 'foreground' , imName + '.png'), foreground)
            cv2.imwrite(os.path.join(GRABCUT_DIR , 'background' , imName + '.png'), background)

    pbar.finish()

    ###########################################################################################################################################
    # extracts 13-dim Haralick texture and color histogram from fore- and background of images -- WARNING: this script takes hours to complete
    ###########################################################################################################################################
    plt.style.use('seaborn-dark')

    def make_fg_bg_hist_plot(fg, bg):
        # make a plot comparing color histograms of foreground to background
        f, axarr = plt.subplots(2, 2)
        b, g, r, a = cv2.split(fg)
        bData = numpy.extract(a>0, b)
        gData = numpy.extract(a>0, g)
        rData = numpy.extract(a>0, r)
        axarr[0,0].set_title("Foreground")
        axarr[0,0].set_ylabel("Normalized # of pixels")
        for chan, col in zip([rData, gData, bData], ['red', 'green', 'blue']):
            hist = cv2.calcHist([chan], [0], None, [256], [0, 256])
            hist /= hist.sum() # normalize to compare images of different sizes
            axarr[0,0].plot(hist, color = col)
            axarr[0,0].set_xlim([0, 256])

        b, g, r, a = cv2.split(bg)
        bData = numpy.extract(a>0, b)
        gData = numpy.extract(a>0, g)
        rData = numpy.extract(a>0, r)
        axarr[0,1].set_title("Background")
        for chan, col in zip([rData, gData, bData], ['red', 'green', 'blue']):
            hist = cv2.calcHist([chan], [0], None, [256], [0, 256])
            hist /= hist.sum() # normalize to compare images of different sizes
            axarr[0,1].plot(hist, color = col)
            axarr[0,1].set_xlim([0, 256])
        axarr[1,0].imshow(cv2.cvtColor(fg, cv2.COLOR_BGRA2RGBA))
        axarr[1,1].imshow(cv2.cvtColor(bg, cv2.COLOR_BGRA2RGBA))
        # plt.show()

    def get_fg_bg_color_hists(fg, bg):
        # returns normalized histograms of color for 
        b, g, r, a = cv2.split(fg)
        bData = numpy.extract(a>0, b)
        gData = numpy.extract(a>0, g)
        rData = numpy.extract(a>0, r)
        fgHist = {}
        for chan, col in zip([rData, gData, bData], ['red', 'green', 'blue']):
            fgHist[col] = cv2.calcHist([chan], [0], None, [256], [0, 256])
            fgHist[col] /= fgHist[col].sum() # normalize to compare images of different sizes

        b, g, r, a = cv2.split(bg)
        bData = numpy.extract(a>0, b)
        gData = numpy.extract(a>0, g)
        rData = numpy.extract(a>0, r)
        bgHist = {}
        for chan, col in zip([rData, gData, bData], ['red', 'green', 'blue']):
            bgHist[col] = cv2.calcHist([chan], [0], None, [256], [0, 256])
            bgHist[col] /= bgHist[col].sum() # normalize to compare images of different sizes
        
        return fgHist, bgHist

    def get_fg_bg_rects(fg):
        b, g, r, a = cv2.split(fg)
        h, w = fg.shape[:2]
        h -= 1
        w -= 1 # to avoid indexing problems
        rectDims = [10, 10] # h, w of rectangles
        hRects = h // rectDims[0]
        wRects = w // rectDims[1]
        fgRects = []
        bgRects = []
        for i in range(wRects):
            for j in range(hRects):
                pt1 = (i * rectDims[0], j * rectDims[1])
                pt2 = ((i + 1) * rectDims[0], (j + 1) * rectDims[1])
                # alpha is 255 over the part of the animal
                if a[pt1[1], pt1[0]] == 255 and a[pt2[1], pt2[0]] == 255:
                    fgRects.append([pt1, pt2])
                    #cv2.rectangle(fgcp, pt1, pt2, [0, 0, 255], 2) # for debugging
                elif a[pt1[1], pt1[0]] == 0 and a[pt2[1], pt2[0]] == 0:
                    bgRects.append([pt1, pt2])
                    #cv2.rectangle(bgcp, pt1, pt2, [0, 0, 255], 2)
        
        return fgRects, bgRects

    def get_avg_hara(im, rects):
        # returns the haralick texture averaged over all rectangles in an image
        if len(rects)==0:
            return None
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        hara = 0
        for r in rects:
            # slice images as: img[y0:y1, x0:x1]
            hara += haralick(im[r[0][1]:r[1][1], r[0][0]:r[1][0]]).mean(0)
        hara /= (len(rects))
        return hara

    def do_analysis(i, breed):
        nonlocal histNtext, rowCnt, pbar
        cropDir = os.path.join(TRAINING_DATA , breed , 'grabcut')
        fgDir = os.path.join(cropDir , 'foreground')
        bgDir = os.path.join(cropDir , 'background')
        fgFiles = os.listdir(fgDir)

        for fi in fgFiles:
            print(fi)
            try:
                # just in case we have maxval wrong in the pbar
                pbar.update(i)
            except:
                pass
            try:
                fg = cv2.imread(os.path.join(fgDir , fi), -1)
                bg = cv2.imread(os.path.join(bgDir , fi), -1) # -1 tells it to load alpha channel
            except:
                continue
            if fg.all()!=None and bg.all()!=None:
                if rowCnt == 0:
                    make_fg_bg_hist_plot(fg, bg)
                if fg.shape[1] > 450:
                    fg = imutils.resize(fg, width = 450)
                    bg = imutils.resize(bg, width = 450)
                fgRects, bgRects = get_fg_bg_rects(fg)
                fgHara = get_avg_hara(fg, fgRects)
                # to speed up the process, comment the following line--we don't use the bg for ML
                bgHara = get_avg_hara(bg, bgRects)
                fgHist, bgHist = get_fg_bg_color_hists(fg, bg)
                if None in [fgRects, bgRects, fgHara.all(), bgHara.all()]:
                    continue
                histNtext.loc[rowCnt] = [breed, fi, fgHara, bgHara, fgHist, bgHist]
                rowCnt += 1
        
        pickle.dump(histNtext, open(os.path.join(PICKLE_MODELS , 'histNtext-fg+bg.pd.pk'), 'wb'))
        pbar.update(i)

    bb = pickle.load(open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes-clean.pd.pk'), 'rb'))
    bb.dropna(inplace=True)

    widgets = ["Calculating Haralick features: ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
    pbar = progressbar.ProgressBar(maxval=bb.shape[0], widgets=widgets).start()

    rowCnt = 0
    histNtext = pandas.DataFrame(columns=['breed', 'file', 'fgHaralick', 'bgHaralick', 'fgHist', 'bgHist'])

    for i, breed in enumerate(sorted(bb.breed.unique().tolist())):
        do_analysis(i, breed)

    # to do this with multithreading, uncomment this
    #p = Pool(8)
    #p.map(do_analysis, list(sorted(bb.breed.unique().tolist())))

    pbar.finish()

    # #######################################################################
    # #Extract the 52-dimension Haralick features of only the foregrounds.
    # #######################################################################

    def get_fg_color_hists(fg):
        # returns normalized histograms of color for 
        r, g, b, a = cv2.split(fg)
        bData = numpy.extract(a>0, b)
        gData = numpy.extract(a>0, g)
        rData = numpy.extract(a>0, r)
        fgHist = {}
        for chan, col in zip([rData, gData, bData], ['red', 'green', 'blue']):
            fgHist[col] = cv2.calcHist([chan], [0], None, [256], [0, 256])
            fgHist[col] /= fgHist[col].sum() # normalize to compare images of different sizes
        
        return fgHist

    def get_fg_rects(fg):
        b, g, r, a = cv2.split(fg)
        h, w = fg.shape[:2]
        h -= 1
        w -= 1 # to avoid indexing problems
        rectDims = [10, 10] # w, h of rectangles
        hRects = h // rectDims[0]
        wRects = w // rectDims[1]
        fgRects = []
        for i in range(wRects):
            for j in range(hRects):
                pt1 = (i * rectDims[0], j * rectDims[1])
                pt2 = ((i + 1) * rectDims[0], (j + 1) * rectDims[1])
                # alpha is 0 over the part of the animal
                if a[pt1[1], pt1[0]] == 255 and a[pt2[1], pt2[0]] == 255:
                    fgRects.append([pt1, pt2])
        
        return fgRects

    def do_analysis(breed):
        nonlocal histNtext, rowCnt, pbar
        cropDir = os.path.join(TRAINING_DATA , breed , 'grabcut')
        fgDir = os.path.join(cropDir , 'foreground')
        fgFiles = os.listdir(fgDir)

        for fi in fgFiles:
            try:
                fg = cv2.imread(os.path.join(fgDir , fi), -1) # -1 tells it to load alpha channel
            except: # some weren't reading properly
                continue
            if fg.all()!=None:
                if fg.shape[1] > 450:
                    fg = imutils.resize(fg, width = 450)
                fgRects = get_fg_rects(fg)
                fgHara = get_avg_hara(fg, fgRects)
                fgHist = get_fg_color_hists(fg)
                if None in [fgRects, fgHara.all()]:
                    continue
                histNtext.loc[rowCnt] = [breed, fi, fgHara]
                rowCnt += 1
                try:
                    pbar.update(rowCnt)
                except:
                    pass
        
        pickle.dump(histNtext, open(os.path.join(PICKLE_MODELS , 'fgHara-full-13x4.pd.pk'), 'wb'))

    bb = pickle.load(open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes-clean.pd.pk'), 'rb'))
    bb.dropna(inplace=True)

    widgets = ["Calculating Haralick features: ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
    pbar = progressbar.ProgressBar(maxval=1480, widgets=widgets).start() # think maxval should be bb.shape[0]*6.3, but know its 1459 post-mortem

    rowCnt = 0
    histNtext = pandas.DataFrame(columns=['breed', 'file', 'fgHaralick'])

    for i, breed in enumerate(sorted(bb.breed.unique().tolist())):
        do_analysis(breed)

    # to do this with multithreading, uncomment this
    #p = Pool(8)
    #p.map(do_analysis, list(sorted(bb.breed.unique().tolist())))

    ############################################################################
    # Extract the color histograms of only the foregrounds.
    ############################################################################

    bb = pickle.load(open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes-clean.pd.pk'), 'rb'))
    bb.dropna(inplace=True)

    widgets = ["Calculating Haralick features: ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
    pbar = progressbar.ProgressBar(maxval=1507, widgets=widgets).start() # think maxval should be aronudd bb.shape[0]*6.3, but know its 1507 post-mortem

    rowCnt = 0
    hists = pandas.DataFrame(columns=['breed', 'file', 'fgHist'])

    breeds = list(sorted(bb.breed.unique().tolist()))

    for breed in breeds:
        cropDir = os.path.join(TRAINING_DATA , breed , 'grabcut')
        fgDir = os.path.join(cropDir , 'foreground')
        fgFiles = os.listdir(fgDir)
        
        for fi in fgFiles:
            try:
                fg = cv2.imread(os.path.join(fgDir , fi), -1) # -1 tells it to load alpha channel
            except: # some weren't reading properly
                continue
            # print(fgDir + fi, -1)
            if fg.all()!=None:
                if fg.shape[1] > 450:
                    fg = imutils.resize(fg, width = 450)
                fgHist = get_fg_color_hists(fg)
                if None in [fgHist]:
                    continue
                hists.loc[rowCnt] = [breed, fi, fgHist]
                rowCnt += 1
                try:
                    pbar.update(rowCnt)
                except:
                    pass
        
        pickle.dump(hists, open(os.path.join(PICKLE_MODELS , 'fgHists.pd.pk'), 'wb'))

    ################################################################################
    # # performs PCA on Haralick, does some analysis on PCA and color histograms
    ################################################################################

    def show_examples(idxs, printStd=True):
        # prints example dataset from supplied indexs, idxs
        # and plots the foreground haralick features
        x = list(range(1,14))
        xs = []
        hara = []
        breed = []

        for idx in idxs:
            a = hNt.iloc[idx]
            xs.append(x)
            hara.append(numpy.log(abs(a.fgHaralick)))
            breed.append([a.breed] * 13)
            
            if printStd:
                print('breed:', a.breed)
                print('filename:', a.file)
                print('foreground Haralick:', a.fgHaralick)
                print('background Haralick:', a.bgHaralick)
        
        newDF = pandas.DataFrame(columns=['Haralick feature', 'log(Haralick feature value)', 'breed'])
        newDF['Haralick feature'] = numpy.array(xs).flatten()
        newDF['log(Haralick feature value)'] = pandas.Series(numpy.array(hara).flatten())
        newDF['breed'] = numpy.array(breed).flatten()
        newDF.sort_values(by='breed', inplace=True)
        sns.lmplot(x='Haralick feature', y='log(Haralick feature value)', data=newDF, fit_reg=False, hue='breed')
        plt.xticks(x)
        # plt.show()

    def get_hara_stats(df):
        # gets statistics on haralick features
        # takes dataframe with haralick and breeds
        x = list(range(1,14))
        xs = []
        haraFG = []
        breed = []
        for i in range(df.shape[0]):
            a = df.iloc[i]
            xs.append(x)
            haraFG.append(a.fgHaralick)
            breed.append([a.breed]*13)
        
        newDF = pandas.DataFrame(columns=['Haralick feature', 'Haralick feature value', 'breed'])
        newDF['Haralick feature'] = numpy.array(xs).flatten()
        newDF['Haralick FG feature value'] = pandas.Series(numpy.array(haraFG).flatten())
        newDF['breed'] = numpy.array(breed).flatten()
        stds = []
        for i in x:
            stds.append(newDF[newDF['Haralick feature']==i]['Haralick FG feature value'].std()
                        / newDF[newDF['Haralick feature']==i]['Haralick FG feature value'].mean())
        
        data = numpy.vstack((numpy.array(x), numpy.array(stds))).T
        pltDF = pandas.DataFrame(columns=['Haralick feature', 'relative standard deviation'], data=data)
        sns.lmplot(x='Haralick feature', y='relative standard deviation', data=pltDF, fit_reg=False)
        plt.xticks(x)
        # plt.show()

    def getOutliers(df):
        # calculates quartiles and gets outliers
        outliers = []
        feats = []
        outlierDict = {}
        # only care about the first 3 dims
        features = ['Dim{}'.format(i) for i in range(1, 3)]
        for feature in features:
            Q1 = numpy.percentile(df[feature], 25)
            Q3 = numpy.percentile(df[feature], 75)
            step = (Q3-Q1) * 1.5
            newOutliers = df[~((df[feature] >= Q1 - step) & (df[feature] <= Q3 + step))].index.values
            outliers.extend(newOutliers)
            feats.extend(newOutliers.shape[0] * [feature])
            for out in newOutliers:
                outlierDict.setdefault(out, []).append(feature)
        
        return sorted(list(set(outliers))), zip(outliers, feats), outlierDict

    histNtext = pickle.load(open(os.path.join(PICKLE_MODELS , 'histNtext-fg+bg.pd.pk'), 'rb'))
    histNtext.reset_index(inplace=True)
    hNt = histNtext

    # This section was necessary when I forgot to add in the breed information
    # the first time working through this.  It shouldn't be necessary now.
    if 'breed' not in histNtext.columns:
        bb = pickle.load(open(os.path.join(PICKLE_MODELS , 'pAnimals-bounding-boxes-clean.pd.pk'), 'rb'))
        bb.dropna(inplace=True)
        bb.reset_index(inplace=True)

        # make column of just filename in breed/bounding box DF
        files = []
        for i in range(bb.shape[0]):
            imName = bb.iloc[i].path.split('/')[-1]
            ext = re.search('\.\w', imName)
            if ext:
                imName = imName.split('.')[0]
            elif imName[-1]=='.':
                imName = imName[:-1]
            files.append(imName)

        bb['raw_file_name'] = pandas.Series(files)

        # add raw filename column to histogram and haralick texture DF
        files = []
        for i in range(histNtext.shape[0]):
            files.append(histNtext.iloc[i].file[:-4])

        histNtext['raw_file_name'] = pandas.Series(files)

        # add breed info to histNtext DF
        hNt = histNtext.merge(bb[['breed', 'raw_file_name']], on='raw_file_name')
        hNt.drop('index', 1, inplace=True)
        hNt.reset_index(inplace=True)
        hNt.drop('index', 1, inplace=True)
        # save to pickle file so we don't have to do this again
        pickle.dump(hNt, open(os.path.join(PICKLE_MODELS , 'histNtext-fg+bg.pd.pk'), 'wb'))

    # # uncomment to show examples:
    # show_examples([0,3])

    # # uncomment to plot foreground haralick standard deviations
    # get_hara_stats(hNt)

    # make dataframes with each component of haralick texture as a column
    bgHDF = pandas.DataFrame(index=range(hNt.shape[0]), columns=['background{}'.format(i) for i in range(1,14)] + ['breed'])
    fgHDF = pandas.DataFrame(index=range(hNt.shape[0]), columns=['foreground{}'.format(i) for i in range(1,14)] + ['breed'])

    # transform the data by taking the log because it varies over orders of magnitude
    # also need to take absolute value because some values are negative

    for i in range(hNt.shape[0]):
        for j in range(13):
            bgHDF.iloc[i,j] = numpy.log(abs(hNt.iloc[i]['bgHaralick'][j]))
            fgHDF.iloc[i,j] = numpy.log(abs(hNt.iloc[i]['fgHaralick'][j]))
        bgHDF.iloc[i]['breed'] = hNt.iloc[i].breed
        fgHDF.iloc[i]['breed'] = hNt.iloc[i].breed

    # fit PCA to the data
    pcaBG = PCA(n_components=2)
    pcaBG.fit(bgHDF.drop('breed', 1))
    pcaFG = PCA(n_components=2)
    pcaFG.fit(fgHDF.drop('breed', 1))
    varianceBG = pcaBG.explained_variance_ratio_
    varianceFG = pcaFG.explained_variance_ratio_
    # about 95% of the variance is captured by the first 3 components of PCA

    # save pcaFG fit for later use
    pickle.dump(pcaFG, open(os.path.join(PICKLE_MODELS , 'pcaFG.pk'), 'wb'))

    # plot cumulative distribution of PCA componenents
    serBG = pandas.Series(varianceBG)
    serBG = serBG.cumsum()
    serFG = pandas.Series(varianceFG)
    serFG = serFG.cumsum()
    dims = numpy.array(['Dim{}'.format(i) for i in range(1,3)]*2)
    labels = ['foreground']*2 + ['background']*2
    bgDF = pandas.DataFrame(numpy.vstack((dims, numpy.hstack((serFG, serBG)), labels)).T, columns = ['dimension', 'cumulative sum', 'location'])
    bgDF['cumulative sum'] = bgDF['cumulative sum'].astype('float64')
    '''f, ax = plt.subplots(1,1)
    sns.pointplot(x=['Dim{}'.format(i) for i in range(1,7)], y=serBG, color='black', ax=ax, label='background')
    g = sns.pointplot(x=, y=serFG, color='red', ax=ax, label='foreground')'''
    sns.catplot(x='dimension', y='cumulative sum', data=bgDF, hue='location')
    ax = plt.gca()
    ax.set_ylim([0.5,1.05])
    ax.set_title('variance contribution of PCA features')
    # plt.show()


    # transform the data with our PCA
    reduced_data_BG = pandas.DataFrame(numpy.hstack((pcaBG.transform(bgHDF.drop('breed', 1)), bgHDF.breed[:, numpy.newaxis])), 
                                columns=['Dim{}'.format(i) for i in range(1,3)] + ['breed'])
    reduced_data_FG = pandas.DataFrame(numpy.hstack((pcaBG.transform(fgHDF.drop('breed', 1)), fgHDF.breed[:, numpy.newaxis])), 
                                columns=['Dim{}'.format(i) for i in range(1,3)] + ['breed'])

    # need an 'index' column to be able to merge with breed info
    # did this the first time through, shouldn't be necessary now
    '''
    reduced_data_BG.reset_index(inplace=True)
    new_BG = reduced_data_BG.merge(hNt[['index', 'breed']], on='index')
    reduced_data_FG.reset_index(inplace=True)
    new_FG = reduced_data_FG.merge(hNt[['index', 'breed']], on='index')
    '''

    # analyze outliers
    outliers, outFeats, outDict = getOutliers(reduced_data_FG)
    # we only care about outliers in more than one dim
    throwOut = []
    for k, v in outDict.items():
        if len(v) > 1:
            throwOut.append(k)

    reduced_data_FG = reduced_data_FG.drop(reduced_data_FG.index[throwOut]).reset_index(drop = True)

    pickle.dump(reduced_data_FG, open(os.path.join(PICKLE_MODELS , 'training_data-13dimHaraFG-PCA.pd.pk'), 'wb'))

    bb = pickle.load(open(os.path.join(PICKLE_MODELS , 'training_data-13dimHaraFG-PCA.pd.pk'), 'rb'))
    bb.dropna(inplace=True)

    Tdata = bb.drop('breed', 1)
    return numpy.array([[i for i in Tdata.iloc[0, :3]]])
