from HTMLParser import HTMLParser
from glob import glob
from tqdm import tqdm

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def main():
	files = glob('../benchmark sources/*')
	print "Files - ",files
	for filen in tqdm(files):
		txt = open(filen).read()
		print "Txt - ",txt
		with open(filen, 'w') as of:
			of.write(HTMLParser().unescape(txt))

if __name__ == '__main__':
	main()