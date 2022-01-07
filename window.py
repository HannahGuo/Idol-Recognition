"""
Where all the magic happens.

I started with the following tutorials and altered the code for my use case:
https://www.youtube.com/watch?v=535acCxjHCI
https://github.com/ageitgey/face_recognition/blob/master/examples/recognize_faces_in_pictures.py
"""

import tkinter.ttk as ttk
from pathlib import Path
from tkinter import *
from tkinter.scrolledtext import ScrolledText

import pyglet
import cv2
import face_recognition
import numpy
import os
import sys
from PIL import ImageGrab

BACKGROUND_COLOR = "#E3817E"
WINDOW_WIDTH = 380
WINDOW_HEIGHT = 300
FONT_FACE = "Garet Book"
FONT_COLOR = "white"
KNOWN_FACES_DIR = "training_faces"
UNKNOWN_FACES_DIR = "unknown_faces"
NUM_JITTERS = 1
TOLERANCE = 0.45
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = "hog"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller
    Taken directly from https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    """
    Taken directly from https://stackoverflow.com/questions/44650888/resize-an-image-without-distortion-opencv/52796112
    :param image:
    :param width:
    :param height:
    :param inter:
    :return:
    """
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation=inter)
    return resized


def save_faces(group):
    """
    Converts and saved image files into npy files. This makes loading *much* faster. This function only needs to be
    run once for an initial conversion. This function is set up so that the images are directly under with a numpy array
    e.g. training_faces -> BTS -> JHOPE -> <image files> and numpy folder

    :param group: Name of group to save.
    """
    group = group.upper()
    group_dir = Path(KNOWN_FACES_DIR, group)

    print("Saving known faces")

    for name in os.listdir(group_dir):
        for filename in os.listdir(Path(group_dir, name)):
            if filename == "numpy":  # skip numpy folder
                continue

            print(filename)
            image = face_recognition.load_image_file(Path(group_dir, name, filename))
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) == 1:
                encoding = face_recognition.face_encodings(image)[0]
                new_file_name = filename.split(".")[0]

                if not Path(group_dir, name, "numpy").is_dir():
                    os.mkdir(Path(group_dir, name, "numpy"))

                if not Path(group_dir, name, "numpy", new_file_name).is_file():
                    numpy.save(str(Path(group_dir, name, "numpy", new_file_name)), encoding)
            else:
                print("INVALID FILE", name, filename)

    print("Known faces for group", group, "saved!")


def load_groups():
    all_groups = []
    for name in os.listdir(resource_path("./training_faces")):
        all_groups.append(name)
    return all_groups


def get_screenshot():
    """
    Takes a screenshot and returns it
    :return: A screenshot of the image as a numpy array
    """
    img = ImageGrab.grab()  # bbox specifies specific region (bbox= x,y,width,height)
    img_np = numpy.array(img)
    return img_np


class AppWindow:
    def __init__(self):
        self.root = Tk()
        self.root.title("Idol Recognition")
        self.root.iconbitmap(resource_path("favicon.ico"))

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        offset_x = int(screen_width - WINDOW_WIDTH - 20)
        offset_y = int(40)

        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{offset_x}+{offset_y}')

        self.root.configure(background=BACKGROUND_COLOR)
        self.root.resizable(False, False)

        # Main Frame
        frame = Frame(self.root, bg=BACKGROUND_COLOR, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        title = Label(self.root,
                      text="Idol Recognition",
                      bg=BACKGROUND_COLOR,
                      font=(FONT_FACE, 28),
                      fg=FONT_COLOR)
        title.grid(column=0, columnspan=2, row=0, sticky="NESW", pady=(20, 0))

        # Left Frame Content (except for Button which is below)
        settings_label = Label(frame,
                               text="Settings",
                               bg=BACKGROUND_COLOR,
                               font=(FONT_FACE, 14),
                               fg=FONT_COLOR,
                               anchor="center")
        settings_label.grid(sticky="NESW", column=0, row=1, pady=(0, 10))

        group_options = load_groups()
        self.known_faces = {}

        for g in group_options:
            self.load_faces(g)

        group_options = list(self.known_faces.keys())

        print("Known faces loaded!")

        self.group_var = StringVar(frame)

        w = ttk.OptionMenu(frame, self.group_var, "Select Group", *group_options)
        w.configure(width=12)
        w.grid(sticky="NESW", column=0, row=2, pady=(0, 10))

        # Right Frame
        breakdown_label = Label(frame,
                                text="Image Breakdown",
                                bg=BACKGROUND_COLOR,
                                font=(FONT_FACE, 14),
                                fg=FONT_COLOR,
                                anchor="w")
        # TODO: how on earth to tkinter grids works why won't this label center
        breakdown_label.grid(sticky="w", column=1, row=1, rowspan=1, padx=40, pady=(0, 10))

        self.breakdown_scroll = ScrolledText(frame, undo=True, height=10, width=22)
        self.insert_breakdown("...")
        self.breakdown_scroll.grid(column=1, row=2, rowspan=2, padx=30)

        # Button (left frame)
        self.enter_button = Button(frame, text="Scan Screen", command=self.match_faces_ss, height=6,
                                   highlightthickness=0, bd=0)
        self.enter_button.grid(column=0, row=3, sticky='nesw', pady=(10, 0))

        frame.grid(sticky="nesw", padx=20, pady=20)
        self.root.mainloop()

    def get_group_var(self):
        return self.group_var.get()

    def insert_breakdown(self, text):
        self.breakdown_scroll.configure(state='normal')
        self.breakdown_scroll.delete('0.0', END)
        self.breakdown_scroll.insert(INSERT, text)
        self.breakdown_scroll.configure(state='disabled')
        self.root.update()

    def add_to_breakdown(self, text):
        self.breakdown_scroll.configure(state='normal')
        self.breakdown_scroll.insert(INSERT, text)
        self.breakdown_scroll.configure(state='disabled')
        self.root.update()

    def match_faces_ss(self):
        """
        Runs facial recognition on the faces found in the image and attempts to match them
        """
        group = self.get_group_var()
        print("g", group)

        lg = load_groups()
        if group not in lg:
            self.insert_breakdown("No group selected!")
            return

        image = get_screenshot()
        self.insert_breakdown("Processing screen for group " + group + "...")
        self.disable_screenshot_button()

        print("Loading unknown faces")

        results = {}
        # results structure:
        # {
        #     "filename": {
        #         "image": <image>,
        #         "num_faces" int,
        #         "faces" : [
        #             {
        #                 "face_box" : <face_location_rect>
        #                 "possible identities": {"match name": [ratings(true / false array depending on match)]},
        #             }
        #         ]
        #     }
        # }

        locations = face_recognition.face_locations(image, model=MODEL)
        encodings = face_recognition.face_encodings(image, locations, num_jitters=NUM_JITTERS)

        if len(encodings) == 0:
            self.insert_breakdown("No faces found,\nplease try again")
            self.enable_screenshot_button()
            return

        image_cv = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        file_key = "screenshotted_image"

        if file_key not in results:
            results[file_key] = {}

        results[file_key]["num_faces"] = len(encodings)
        results[file_key]["image"] = image_cv
        results[file_key]["faces"] = []

        for face_encoding, face_location in zip(encodings, locations):
            new_face_item = {
                "face_box": face_location,
                "possible_ids": {}
            }

            group = group.upper()

            for kf_key in self.known_faces[group]:
                compare_results = face_recognition.compare_faces(self.known_faces[group][kf_key],
                                                                 face_encoding, TOLERANCE)
                new_face_item["possible_ids"][kf_key] = compare_results

            results[file_key]["faces"].append(new_face_item)

        self.insert_breakdown("")
        for fn in results:
            image = results[fn]["image"]
            print("Showing Results for file:", fn)
            print(results[fn]["num_faces"], "faces found in image")

            for ff_ind, face_found in enumerate(results[fn]["faces"]):
                face_location = face_found["face_box"]
                face_results = {
                    # ordered from most to least matches
                    "identity": "",
                    "matches": 10,
                    # minimum matches threshold to accept as a match (arbitrarily set)
                }

                for mn in face_found["possible_ids"]:
                    total_matches = sum(face_found["possible_ids"][mn])
                    # assume it's accurate enough that = won't happen often
                    if face_results["matches"] <= total_matches:
                        face_results["identity"] = mn
                        face_results["matches"] = total_matches

                color = [0, 255, 0]
                if not face_results["identity"]:
                    self.add_to_breakdown("No matches for face " + str(ff_ind) + "\n")

                    # text rectangle
                    top_left = (face_location[3], face_location[2])
                    bottom_right = (face_location[1], face_location[2] + 22)
                    cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
                    cv2.putText(image, str(ff_ind) + ".", (face_location[3] + 10, face_location[2] + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), FONT_THICKNESS)
                else:
                    found_identity = face_results["identity"]
                    print("Most accurate guess: ", found_identity)

                    # face rectangle
                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])
                    cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

                    # text rectangle
                    top_left = (face_location[3], face_location[2])
                    bottom_right = (face_location[1], face_location[2] + 22)
                    cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
                    cv2.putText(image, str(ff_ind) + "." + found_identity,
                                (face_location[3] + 10, face_location[2] + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), FONT_THICKNESS)

                self.add_to_breakdown("Face " + str(ff_ind) + " Breakdown\n")
                for identity in face_found["possible_ids"]:
                    total_matches_each = sum(face_found["possible_ids"][identity])
                    self.add_to_breakdown(identity + " " + str(total_matches_each) + "/50\n")

                self.add_to_breakdown(("*" * 18) + "\n")

            image = image_resize(image, height=800)

            cv2.namedWindow(fn, cv2.WINDOW_NORMAL)
            cv2.moveWindow(fn, 40, 30)
            cv2.imshow(fn, image)
            cv2.waitKey(200)
            self.enable_screenshot_button()
            self.root.update()

    def load_faces(self, group):
        """
        Loads numpy arrays (stored in npy files) into known_faces.
        :param group: Name of group to load
        """
        group = group.upper()
        group_dir = resource_path(KNOWN_FACES_DIR + "/" + group)

        print("Loading known faces")

        for name in os.listdir(group_dir):
            if not os.path.isdir(Path(group_dir, name, "numpy")):
                print("Broken directory for numpy", group_dir, name)
                continue

            for filename in os.listdir(Path(group_dir, name, "numpy")):
                print(filename)

                if group not in self.known_faces:
                    self.known_faces[group] = {}

                if name not in self.known_faces[group]:
                    self.known_faces[group][name] = []

                self.known_faces[group][name].append(numpy.load(str(Path(group_dir, name, "numpy", filename))))

    def disable_screenshot_button(self):
        self.enter_button.configure(state=DISABLED)
        self.root.update()

    def enable_screenshot_button(self):
        self.enter_button.configure(state=ACTIVE)
        self.root.update()

    def quit_window(self):
        self.root.quit()
        self.root.destroy()


if __name__ == '__main__':
    pyglet.font.add_file(resource_path("Garet-Book.ttf"))
    new_app_window = AppWindow()
