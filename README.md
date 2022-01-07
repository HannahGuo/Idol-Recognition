<p align="center" >
    <img src="/app_images/2.png" width="300" height="300">
</p>

# Idol Recognition
Idol Recognition is a Python application that uses facial recognition to identify k-pop idols from an image.

Massive thanks to [sentdex's tutorial](https://pythonprogramming.net/facial-recognition-python/) for giving me a starting point.

## Installation
### Running the Project
Follow all the initial installation instructions [here](https://pythonprogramming.net/facial-recognition-python/#General-Installation-Information) (bonus steps not required).

In addition, install (using pip or another package-management system):
- `pyglet`
- `opencv-python`

### Using the Executable
Alternatively, this project can be compiled into a .exe executable (only tested on Windows 10).

If you'd like to compile the executable yourself, after completing all the installation instructions above, then:
- Install `pyinstaller`
- Locate the `face_recognition_models` folder (likely in your venv/Lib/site-packages folder )and copy it into this directory (i.e. same level as training_faces) 
  - If you can't find it, download it from here [face_recognition_models](https://github.com/ageitgey/face_recognition_models)
- Locate the `.lib` folder nested inside the `scipy` folder. This could be in the same place as `face_recognition_models`, or in `C:\Users\{your_user}\AppData\Roaming\Python\{python version}\site-packages\scipy`. Copy it the same way as you did before.
- Run `pyinstaller window.spec` (it'll take a minute or two)
- The executable will be in the `build` folder.

*Note that PyInstaller has a thing where [it may be seen as a trojan by your antivirus](https://stackoverflow.com/questions/43777106/program-made-with-pyinstaller-now-seen-as-a-trojan-horse-by-avg). There is no malicious code in this project (see all the files), but if this is an issue you can try out the code on the `console_approach` branch (which doesn't use Pyinstaller) or download the .exe directly. The given .exe should not raise a virus error.*


## Project Structure
### Main Branch
- `/app_images`: images for the README
- `/training_faces`: numpy files for idol images
- `favicon.ico`: the favicon for the window
- `Garet-Brook.ttf`: the font used for the window
- `window.py`: the main Python file
- `window.spec`: the spec file used by [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/usage.html) to compile an exe 

### Console Approach Branch
Similar to main branch but with no window. This was the code I used when first developing the app, and uses keypresses to take screenshots. 

### Training Data Branch
All the images used. These are converted into numpy arrays so that they can be loaded faster (and aren't needed once the images have been converted). Still, it's a pretty large data set. 

## How it Works
This project uses the `facial_recognition` library, which handles all the nitty-gritty facial-recognition math so I can just use its function to compare. 

I convert the data set into numpy arrays (using `save_faces`) and run facial recognition on those.

The original tutorial I followed trains images and, as long as there's one match, it returns a positive. However, I was running into problems with false positives, and I also wanted to have my application recognize and match all faces.

After detecting all the faces in the screenshot, the algorithm compares the face to every image for all the members in the selected group. It counts the number of matches, and returns the member with the most matches.

### Wait... so did you manually download 50 images of each member of BTS (and other groups)???
*Weeeeellll*, I started doing them manually (15 images/member)... but then I realized I wanted a larger data set and as much as I like BTS, I wasn't about to do that.

Thankfully, [gallery-dl](https://github.com/mikf/gallery-dl) exists, so I found some Instagram pages and bulk-downloaded before doing some manual filtering/deletion. 

## Program Limitations
- Since I'm using `facial_recognition` to detect faces, if the program doesn't detect faces, it doesn't process them. This can happen when the faces are partially covered or wearing accessories (and some other random cases).
- Multiple idols in the same group may be detected as being the same person (see to-dos) 

## Bugs/To-do List
- [ ] Garet Brook font won't work on Linux systems (due to using pyglet, see [here](https://stackoverflow.com/a/61353191)
- [ ] Fix tkinter alignment (see TODO)
- [ ] Improve UI (tkinter is a bit old-looking :P and has some limitations)
- [ ] Add more groups (if you happen to know an Instagram page or other resource with a lot of clear photos of a member of a group, let me know!)
- [ ] Add a group setting where each member is unique (weighting system to handle ties)

## Credits
- [Garet Font](https://garet.spacetype.co/)
- [Icons from Flaticon.com](https://www.flaticon.com)
- All the libraries mentioned - thank you for existing and making my life easier :)