#!/bin/bash
# © 2023 Roel Roscam Abbing, released as AGPLv3
# see https://www.gnu.org/licenses/agpl-3.0.html
# Support your local low-tech magazine: https://solar.lowtechmagazine.com/donate/

now=`date`
baseURL="https://example.org/" #the URL of the website e.g. htttps://solar.lowtechmagazine.com/
contentDir="/content" #the directory where your HUGO articles are e.g. /path/to/repo/solar_v2/content/
repoDir="/Users/eanna/webdev/solar_v2" #the full path to the repository
outputDir="/Users/eanna/webdev/solar_v2/public" # the directory where you export the site to.


while getopts f flag
do
    case "${flag}" in
        f) updated="forced rebuild";;
    esac
done

if [[ $updated != "forced rebuild" ]]; then
        echo "Checking for update $now"
        updated=$(git -C $repoDir pull origin main)
fi


if  echo $updated | grep -q "Already up to date";
then 
        echo "Git up to date $now"
else
        echo "Git was not up to date"
        echo $updated
        echo "Rebuilding the site"

        cd $repoDir

        echo "Deleting Old Images"
        /usr/bin/python3 utils/dither_images.py -d $contentDir --remove

        echo "Dithering new images"
        /usr/bin/python3 utils/dither_images.py -d $contentDir --colorize

        echo "Calculating page sizes"
        /usr/bin/python3 utils/calculate_size.py --directory $outputDir --baseURL $baseURL

        echo "Generating site"
        hugo -b $baseURL --destination $outputDir

        echo "Calculating page sizes"
        /usr/bin/python3 utils/calculate_size.py --directory $outputDir --baseURL $baseURL

        echo "Removing original media from" $outputDir
        /usr/bin/python3 utils/clean_output.py --directory $outputDir

        after=`date`
        echo "Site regeneration started $now"
        echo "Site regeneration finished $after"
fi
