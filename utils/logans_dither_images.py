# image dithering script
# © 2022 Roel Roscam Abbing, released as AGPLv3
# see https://www.gnu.org/licenses/agpl-3.0.html
# Support your local low-tech magazine: https://solar.lowtechmagazine.com/donate.html 

from hitherdither import palette.Palette
import os
import argparse
import shutil
from PIL import Image
import logging
import random


parser = argparse.ArgumentParser(
    """
    This script recursively traverses folders and creates dithered versions of the images it finds.
    These are stored in the same folder as the images in a folder called "dithers".
    """
)


# these are the allowed argumentd
parser.add_argument(
    '-d', '--directory', help="Set the directory to traverse", default="." 
    )

parser.add_argument(
    '-rm', '--remove', help="Removes all the folders with dithers and their contents", action="store_true" 
    )

parser.add_argument(
    '-c', '--colorize', help="Colorizes the dithered images", action="store_true" 
    )

parser.add_argument(
    '-v', '--verbose', help="logging.debug out more detailed information about what this script is doing", action="store_true" 
    )

args = parser.parse_args()

image_ext = [".jpg", ".JPG", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".bmp"]



# directory to operate in
content_dir = args.directory

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

exclude_dirs = set(["dithers"])


logging.info("Dithering all images in {} and subfolders".format(content_dir))
logging.debug("excluding directories: {}".format("".join(exclude_dirs)))
colors = {
        'low-tech solutions': Palette([(30,32,40), (11,21,71),(57,77,174),(158,168,218),(187,196,230),(243,244,250)]),
        'obsolete technology': Palette([(9,74,58), (58,136,118),(101,163,148),(144,189,179),(169,204,195),(242,247,246)]),
        'high-tech problems': Palette([(86,9,6), (197,49,45),(228,130,124),(233,155,151),(242,193,190),(252,241,240)]),
        'grayscale': Palette([(25,25,25), (75,75,75),(125,125,125),(175,175,175),(225,225,225),(250,250,250)])
        # 'low-tech solutions': Palette([(0, 128, 255), (0, 102, 204), (51, 153, 255),(120, 160, 255), (173, 216, 230), (255, 255, 255)]), this is a pretty blue
        # 'obsolete technology': Palette([(0, 204, 153), (88, 219, 168), (162, 229, 189),(187, 245, 204), (209, 229, 216), (255, 255, 255)]), this is a bright teal
        # 'high-tech problems': Palette([(255, 26, 26), (255, 84, 84), (255, 165, 165),(255, 199, 199), (255, 225, 225), (255, 250, 250)]), this is super saturated red
        # 'grayscale': Palette([(40, 40, 40), (100, 100, 100), (150, 150, 150),(200, 200, 200), (250, 250, 250), (255, 255, 255)])
    }


def colorize(source_image, category):
    """
    Picks a colored dithering palette based on the post category.
    """
    if category: # this runs if a category is defined
        for i in colors.keys():
            if i in category.lower():
                color = colors[i]
                logging.info("Applying color palette '{}' for {}".format(i, category))
                break
            else:
                logging.info("No category for {}, {}".format(source_image, category))
                logging.debug("No category for {}, {}".format(source_image, category))
                color = colors['grayscale']

    else: # this runs is a category is not defined
        logging.info("No category for {}, {}".format(source_image, category))
        logging.debug("No category for {}, {}".format(source_image, category))
        color = colors['grayscale']
        
    return color


def dither_image(source_image, output_image, category ='grayscale'):
    #see hitherdither docs for different dithering algos and settings

    if args.colorize:
        palette = colorize(source_image, category)
    else:
        palette = Palette([
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
])
    try:
        img= Image.open(source_image).convert('RGB')
        img.thumbnail((800,800), Image.LANCZOS)
        #palette = palettes[category]
        threshold = [120, 120, 120]
        img_dithered = hitherdither.ordered.bayer.bayer_dithering(img, palette, threshold, order=8) 
  
        if args.colorize:
          img_dithered = colorize(img_dithered, category)
        logging.debug("Created {} in category {}".format(img_dithered, category))
            
        img_dithered.save(output_image, optimize=True)

    except Exception as e:
        logging.debug("❌ failed to convert {}".format(source_image))
        logging.debug(e)

def delete_dithers(content_dir):
    logging.info("Deleting 'dither' folders in {} and below".format(content_dir))
    for root, dirs, files in os.walk(content_dir, topdown=True):
        if root.endswith('dithers'):
            shutil.rmtree(root)
            logging.info("Removed {}".format(root))
        

def parse_front_matter(md):
    # logging.debug("parsing")
    with open(md) as f:
        contents = f.readlines()
        cat = None
        for l in contents:
            if l.startswith("categories: "):
                cat = l.split("categories: ")[1]
                cat = cat.strip("[")
                cat = cat.strip()
                cat = cat.strip("]")
                cat = cat.strip('"')

                logging.debug("Categories: {} from {}".format(cat, l.strip()))
        # logging.debug(f"{md = }{cat = }")
        return cat

if __name__ == "__main__":
    prev_root = None
    logging.debug("starting main routine")
    if args.remove: # if the command was for removal this runs
        delete_dithers(
            os.path.abspath(content_dir)
            )
    else: # this runs for generation
        logging.debug(f"{os.walk(os.path.abspath(content_dir), topdown=True) = }")

        for root, dirs, files in os.walk(os.path.abspath(content_dir), topdown=True): # runs for every directory under the defined content root
            # root is the fi
            logging.debug("Checking next folder {}".format(root))

            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            category = None
            if prev_root is None:
                prev_root = root

            if prev_root is not root:
                if files:
                    if any(x.endswith(tuple(image_ext)) for x in files):
                        if not os.path.exists(os.path.join(root,'dithers')):
                            os.mkdir(os.path.join(root,'dithers'))
                            logging.info("📁 created in {}".format(root))

            if args.colorize:
                logging.debug(f"{args.colorize}")

                #iterate over md files to find one with a category
                if not category:
                    for i in os.listdir(root):
                        if i.startswith('index'):
                            category = parse_front_matter(os.path.join(root,i))
                            break

            for fname in files:
                if fname.endswith(tuple(image_ext)):
                        file_, ext = os.path.splitext(fname)
                        source_image= os.path.join(root,fname)
                        output_image = os.path.join(os.path.join(root, 'dithers'), file_+'_dithered.png')
                        if not os.path.exists(output_image):
                            if not args.colorize:
                                category = "grayscale"
                                logging.debug("this doesnt run")
                            # logging.debug(f"{args.colorize}")
                            dither_image(source_image,output_image, category)
                            logging.info("🖼 converted {}".format(fname))
                            logging.debug(output_image)
                        else:
                            logging.debug("Dithered version of {} found, skipping".format(fname))

            prev_root = root


    logging.info("Done dithering")
