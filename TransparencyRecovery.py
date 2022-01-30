'''
This tool can convert an image back to its original transparency if it is overlayed with both a white and black background.
This can be useful for getting an accurate image of a games HUD for example.
This only works if the blend/overlay mode is 'normal' (not additive or multiply for example). More modes may be added in the future.
This tool only works with uncompressed TGA.
'''
#togglable options
fileWhite = 'white.tga'
fileBlack = 'black.tga'
fileResult = 'result.tga'

#get hex data
with open(fileWhite, 'rb') as wfile:
	wData = wfile.read().hex(' ')
with open(fileBlack, 'rb') as bfile:
	bData = bfile.read().hex(' ')

#retrieve header
wHeader = wData[:53].split(' ')
bHeader = bData[:53].split(' ')
#gather width height bitdepth and data length of both images
#white
wHeaderWidth = int(wHeader[13] + wHeader[12], 16)
wHeaderHeight = int(wHeader[15] + wHeader[14], 16)
wHeaderDepth = int(wHeader[16], 16)
#black
bHeaderWidth = int(bHeader[13] + bHeader[12], 16)
bHeaderHeight = int(bHeader[15] + bHeader[14], 16)
bHeaderDepth = int(bHeader[16], 16)
#both
headersLen = wHeaderWidth * wHeaderHeight * (wHeaderDepth//8)
#this is mark how long the data (in characters) each pixel is.
if wHeaderDepth == 32:
	pixLen = 12
elif wHeaderDepth == 24:
	pixLen = 9

#test for incompatibilities
if wHeaderWidth == bHeaderWidth and wHeaderHeight == bHeaderHeight and wHeaderDepth == bHeaderDepth:
	pass
else:
	print('width x height x bits of both images do not match. Aborting')
	exit(0)
if wHeader[2] != '02' or bHeader[2] != '02':
	print('Must use uncompressed RGB(A) TGA. (Data type 2). Aborting')
	exit(0)
if wHeaderDepth != 24 and wHeaderDepth != 32:
	print('bits per pixel must be 24 or 32. Aborting')
	exit(0)

#retrieve data block
wData = wData[54:(headersLen * 3) + 54]
bData = bData[54:(headersLen * 3) + 54]

#run through each pixel and create new image
rData = ''
for i in range(wHeaderWidth * wHeaderHeight):
	#put subpixels of each pixel into a list
	wPixel = wData[i*pixLen:(i*pixLen) + 8].split(" ")
	bPixel = bData[i*pixLen:(i*pixLen) + 8].split(" ")
	#calculate result pixel
	pixelOpacity = int(bPixel[0],16) + (255 - int(wPixel[0],16)) #black + (255 - white)
	if pixelOpacity > 255:
		pixelOpacity = 255
		print(f'warning! opacity over 255 at pixel {i}')
	for ii in range(3):
		try:
			subpix = int(int(bPixel[ii],16) * (255 / pixelOpacity))
		except ZeroDivisionError:
			subpix = 0
		if subpix > 255:
			subpix = 255
			print(f'warning! subpixel value over 255 at pixel {i}, subpixel {ii}')
		rData += subpix.to_bytes(1, 'little').hex(' ') + " "
	rData += pixelOpacity.to_bytes(1, 'little').hex(' ') + " "
rData = rData[:-1]
#add header
rData = " ".join(wHeader) + " " + rData
#write to file
with open(fileResult,'wb') as file:
	file.write(bytes.fromhex(rData))
	print(f'finished successfully')