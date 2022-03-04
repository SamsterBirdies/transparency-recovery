'''
This tool can convert an image back to its original transparency if it is overlayed with both a white and black background.
This can be useful for getting an accurate image of a games HUD for example.
This only works if the blend/overlay mode is 'normal' (not additive or multiply for example). More modes may be added in the future.
This tool only works with uncompressed TGA.
'''
import sys
#togglable options
fileWhite = 'white.tga'
fileBlack = 'black.tga'
fileResult = 'result.tga'
logWarnings = 'true'

if len(sys.argv) == 2:
	logWarnings = sys.argv[1]
elif len(sys.argv) == 5:
	logWarnings = sys.argv[1]
	fileWhite = sys.argv[2]
	fileBlack = sys.argv[3]
	fileResult = sys.argv[4]
#get data
with open(fileWhite, 'rb') as wfile:
	wData = bytearray(wfile.read())
with open(fileBlack, 'rb') as bfile:
	bData = bytearray(bfile.read())

#read header
wHeaderWidth = int.from_bytes(wData[12:14], 'little')
wHeaderHeight = int.from_bytes(wData[14:16], 'little')
wHeaderDepth = int(wData[16])

bHeaderWidth = int.from_bytes(bData[12:14], 'little')
bHeaderHeight = int.from_bytes(bData[14:16], 'little')
bHeaderDepth = int(bData[16])

headersLen = wHeaderWidth * wHeaderHeight * (wHeaderDepth//8)

#test for incompatibilities
if wData[2] != 2 or bData[2] != 2:
	print('Must use uncompressed RGB(A) TGA. (Data type 2). Aborting')
	exit(0)
if wHeaderWidth == bHeaderWidth and wHeaderHeight == bHeaderHeight and wHeaderDepth == bHeaderDepth:
	pass
else:
	print('width x height x bits of both images do not match. Aborting')
	exit(0)
if wHeaderDepth != 24 and wHeaderDepth != 32:
	print('bits per pixel must be 24 or 32. Aborting')
	exit(0)
	
#data setup
rData = bytearray(wHeaderWidth * wHeaderHeight * 4 + 18)
for i in range(18):
	rData[i] = wData[i]
rData[16] = 32
subpixels = wHeaderDepth // 8
#run through each pixel and create new image
for i in range(wHeaderWidth * wHeaderHeight):
	#put subpixels of each pixel into a list
	wPixel = [wData[i*subpixels + 18], wData[i*subpixels+19], wData[i*subpixels+20]]
	bPixel = [bData[i*subpixels + 18], bData[i*subpixels+19], bData[i*subpixels+20]]
	#calculate result pixel
	pixelOpacity = int(bPixel[0]) + (255 - int(wPixel[0])) #black + (255 - white)
	if pixelOpacity > 255:
		pixelOpacity = 255
		if logWarnings != 'false':
			print(f'warning! opacity over 255 at pixel {i}')
	for ii in range(3):
		if pixelOpacity != 0:
			subpix = int(int(bPixel[ii]) * (255 / pixelOpacity))
			if subpix > 255:
				subpix = 255
				if logWarnings != 'false':
					print(f'Warning: subpixel {ii} value over 255 at pixel {i}. Clamping')
			rData[i * 4 + ii + 18] = subpix;
		else:
			rData[i * 4 + ii + 18] = 0;
	rData[i * 4 + 21] = pixelOpacity
#write to file
with open(fileResult,'wb') as file:
	file.write(rData)
	print(f'finished successfully')