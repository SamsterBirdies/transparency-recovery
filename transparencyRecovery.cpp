/*
This tool can convert an image back to its original transparency if it is overlayed with both a white and black background.
This can be useful for getting an accurate image of a games HUD for example.
This only works if the blend/overlay mode is 'normal' (not additive or multiply for example). More modes may be added in the future.
This tool only works with uncompressed TGA.
Supports arguments: <log warnings ('true' or 'false')> <white filename> <black filename> <result filename>
*/
#include <iostream>
#include <string>
#include <fstream>
using namespace std;

string fileWhite = "white.tga";
string fileBlack = "black.tga";
string fileResult = "result.tga";
string logWarnings = "true";

int main(int argc, char *argv[]){
	//var
	if (argc == 2){
		logWarnings = argv[1];
	} else if (argc == 5){ //change the filenames if the arguments are given
		logWarnings = argv[1];
		fileWhite = argv[2];
		fileBlack = argv[3];
		fileResult = argv[4];
	}
	streampos size;
	char* wData;
	char* bData;
	//read white
	ifstream fileInputWhite(fileWhite, ios::in|ios::binary|ios::ate);
	if (fileInputWhite.is_open()){
		size = fileInputWhite.tellg();
		wData = new char[size];
		fileInputWhite.seekg(0, ios::beg);
		fileInputWhite.read(wData, size);
		fileInputWhite.close();
	} else {
		cout << "failed to open " << fileWhite <<"\n";
		return 1;
	}
	//read black
	ifstream fileInputBlack(fileBlack, ios::in|ios::binary);
	if (fileInputBlack.is_open()){
		bData = new char[size];
		fileInputBlack.read(bData, size);
		fileInputBlack.close();
	} else {
		cout << "failed to open file\n";
		return 1;
	}
	//read header stats
	const unsigned short int wWidth = (((short)wData[13]) << 8) | (0x00ff & wData[12]);
	const unsigned short int wHeight = (((short)wData[15]) << 8) | (0x00ff & wData[14]);
	const unsigned char wDepth = wData[16];

	const unsigned short int bWidth = (((short)bData[13]) << 8) | (0x00ff & bData[12]);
	const unsigned short int bHeight = (((short)bData[15]) << 8) | (0x00ff & bData[14]);
	const unsigned char bDepth = bData[16];

	//test for incompatibilites
	if (wData[2] != 2 || bData[2] != 2){
		cout << "Must use uncompressed RGB(A) TGA. (Data type 2). Aborting\n";
		return 1;
	}
	if (wWidth == bWidth && wHeight == bHeight && wDepth == bDepth){
	} else {
		cout << "width x height x bits of both images do not match. Aborting\n";
		return 1;
	}
	if (wDepth != 24 && wDepth != 32){
		cout << "bits per pixel must be 24 or 32. Aborting\n";
		return 1;
	}

	//data setup for mainloop
	char* rData = new char[wWidth * wHeight * 4 + 18]; //create new data block
	for (unsigned char i = 0; i < 18; i++){ //header copy
		rData[i] = wData[i];
	}
	rData[16] = 32; //bitdepth must be 32
	unsigned char subpixels = (unsigned char)(wDepth / 8);
	unsigned char* wPixel = new unsigned char[3];
	unsigned char* bPixel = new unsigned char[3];
	unsigned char pixelOpacity;
	float subpix;
	//main loop Run through each pixel and create new image.
	for (unsigned long int i = 0; i < wWidth * wHeight; i++){
		//put relevant subpixels into an array
		wPixel[0] = wData[i*subpixels + 18]; //white blue
		wPixel[1] = wData[i*subpixels + 19]; //white green
		wPixel[2] = wData[i*subpixels + 20]; //white red
		bPixel[0] = bData[i*subpixels + 18]; //black blue
		bPixel[1] = bData[i*subpixels + 19]; //black green
		bPixel[2] = bData[i*subpixels + 20]; //black red

		//calculate opacity
		pixelOpacity = bPixel[0] + (255 - wPixel[0]);
		for (unsigned char ii = 0; ii < 3; ii++){
			if (pixelOpacity != 0){
				subpix = (float)(bPixel[ii] * (float)255/pixelOpacity);
				if (subpix > 255.0) {
					subpix = 255.0;
					if (logWarnings != "false"){
						cout << "Warning: subpixel "<<(int)ii<<" value over 255 at pixel "<<i<<" Clamping\n";
					};
				}
				rData[i * 4 + ii + 18] = (unsigned char)subpix;
			} else {
				rData[i * 4 + ii + 18] = 0;
			}
		}
		rData[i * 4 + 21] = pixelOpacity;
	}	
	//write
	ofstream fileOutputResult(fileResult, ios::out|ios::binary);
	fileOutputResult.write(rData, wWidth * wHeight * 4 + 18);
	fileOutputResult.close();
	cout << "Finished\n";
	return 0;
}