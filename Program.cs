/*
This tool can convert an image back to its original transparency if it is overlayed with both a white and black background.
This can be useful for getting an accurate image of a games HUD for example.
This only works if the blend/overlay mode is 'normal' (not additive or multiply for example). More modes may be added in the future.
This tool only works with uncompressed TGA.
*/

//modifiable options
string fileWhite = "white.tga";
string fileBlack = "black.tga";
string fileOutput = "result.tga";

//get binary data
byte[] wData = File.ReadAllBytes(fileWhite);
byte[] bData = File.ReadAllBytes(fileBlack);

//read header stats
ushort wWidth = BitConverter.ToUInt16(new byte[] {wData[12], wData[13]}, 0);
ushort wHeight = BitConverter.ToUInt16(new byte[] {wData[14], wData[15]}, 0);
byte wDepth = wData[16];

ushort bWidth = BitConverter.ToUInt16(new byte[] {bData[12], bData[13]}, 0);
ushort bHeight = BitConverter.ToUInt16(new byte[] {bData[14], bData[15]}, 0);
byte bDepth = bData[16];

long headersLen = wWidth * wHeight * (wDepth / 8);

//test for incompatibilities
if (wWidth == bWidth && wHeight == bHeight && wDepth == bDepth){
}else{
	Console.WriteLine("width x height x bits of both images do not match. Aborting");
	Environment.Exit(0);
}
if (wData[2] != 2 || bData[2] != 2){
	Console.WriteLine("Must use uncompressed RGB(A) TGA. (Data type 2). Aborting");
	Environment.Exit(0);
}
if (wDepth != 24 && wDepth != 32){
	Console.WriteLine("bits per pixel must be 24 or 32. Aborting");
	Environment.Exit(0);
}

//data setup for mainloop
byte[] rData = new byte[wWidth * wHeight * 4 + 18]; //allocate size
for (byte i = 0; i < 18; i++){ //header copy
	rData[i] = wData[i];
}
rData[16] = 32; //bitdepth must be 32
byte subpixels = (byte)(wDepth / 8);
//main loop. Run through each pixel and create new image.
for (long i = 0; i < wWidth * wHeight; i++){
	//put relevant subpixels into an array
	byte[] wPixel = {wData[i*subpixels + 18], wData[i*subpixels+19], wData[i*subpixels+20]};
	byte[] bPixel = {bData[i*subpixels + 18], bData[i*subpixels+19], bData[i*subpixels+20]};
	//calculate opacity
	byte pixelOpacity = (byte)(bPixel[0] + (255 - wPixel[0]));
	for (byte ii = 0; ii < 3; ii++){
		if (pixelOpacity != 0){
			float subpix = (float)(bPixel[ii] * (float)255/pixelOpacity);
			if (subpix > 255.0f) {
				subpix = 255.0f;
				Console.WriteLine("Warning: subpixel {0} value over 255 at pixel {1}. Clamping",ii,i);
			}
			rData[i * 4 + ii + 18] = Convert.ToByte(subpix);
		} else {
			rData[i * 4 + ii + 18] = 0;
		}
	}
	rData[i * subpixels + 21] = pixelOpacity;
}	
//write
File.WriteAllBytes(fileOutput, rData);
Console.WriteLine("Finished");