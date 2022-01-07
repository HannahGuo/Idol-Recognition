"""
Where all the magic happens.
I started with the following tutorials and altered the code for my use case:
https://www.youtube.com/watch?v=535acCxjHCI
https://github.com/ageitgey/face_recognition/blob/master/examples/recognize_faces_in_pictures.py
"""

import face_recognition
import os
import cv2
from pathlib import Path
from PIL import ImageGrab
import numpy
import keyboard

KNOWN_FACES_DIR = "training_faces"
UNKNOWN_FACES_DIR = "unknown_faces"
NUM_JITTERS = 1
TOLERANCE = 0.45
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = "hog"

known_faces = {}


def save_faces(group):
    """
    Converts and saved image files into npy files. This makes loading *much* faster. This function only needs to be
    run once for an initial conversion.
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


def load_faces(group):
    """
    Loads numpy arrays (stored in npy files) into known_faces.
    :param group: Name of group to load
    :return:
    """
    global known_faces
    group = group.upper()
    group_dir = Path(KNOWN_FACES_DIR, group)

    print("Loading known faces")

    for name in os.listdir(group_dir):
        for filename in os.listdir(Path(group_dir, name, "numpy")):
            print(filename)

            if group not in known_faces:
                known_faces[group] = {}

            if name not in known_faces[group]:
                known_faces[group][name] = []

            known_faces[group][name].append(numpy.load(str(Path(group_dir, name, "numpy", filename))))

    print("Known faces loaded!")


def match_faces_ss(group, image):
    """
    Runs facial recognition on the faces found in the image and attempts to match them
    :param group: Group to check
    :param image: Screenshot of current window
    """
    print("Loading unknown faces")

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

    results = {}

    locations = face_recognition.face_locations(image, model=MODEL)
    encodings = face_recognition.face_encodings(image, locations, num_jitters=NUM_JITTERS)

    if len(encodings) == 0:
        print("no faces found, skipping image")
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

        for kf_key in known_faces[group]:
            compare_results = face_recognition.compare_faces(known_faces[group][kf_key], face_encoding, TOLERANCE)
            new_face_item["possible_ids"][kf_key] = compare_results

        results[file_key]["faces"].append(new_face_item)

    for fn in results:
        image = results[fn]["image"]
        print("Showing Results for file:", fn)
        print(results[fn]["num_faces"], "faces found in image")

        for ff_ind, face_found in enumerate(results[fn]["faces"]):
            face_location = face_found["face_box"]
            face_results = {
                # ordered from most to least matches
                "identity": "",
                "matches": 3,
                # we want the faces to match at least 3 known images to be considered (larger data set would make
                # this more accurate)
            }

            for mn in face_found["possible_ids"]:
                total_matches = sum(face_found["possible_ids"][mn])
                # assume it's accurate enough that = won't happen often
                if face_results["matches"] <= total_matches:
                    face_results["identity"] = mn
                    face_results["matches"] = total_matches

            color = [0, 255, 0]
            if not face_results["identity"]:
                print("No matches found :(")

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
                cv2.putText(image, str(ff_ind) + "." + found_identity, (face_location[3] + 10, face_location[2] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), FONT_THICKNESS)

            print("Recognition Breakdown for face", ff_ind)
            for identity in face_found["possible_ids"]:
                total_matches_each = sum(face_found["possible_ids"][identity])
                print(identity, total_matches_each)

            print("*" * 20)

        cv2.namedWindow(fn, cv2.WINDOW_NORMAL)
        cv2.imshow(fn, image)
        cv2.waitKey(0)
        # cv2.destroyWindow(fn)


def get_screenshot():
    """
    Takes a screenshot and returns it
    :return: A screenshot of the image as a numpy array
    """
    img = ImageGrab.grab()  # bbox specifies specific region (bbox= x,y,width,height)
    img_np = numpy.array(img)
    return img_np


if __name__ == "__main__":
    # run this once to create numpy for images
    # save_faces("BTS")

    # Could technically be put in the match_faces_ss function
    # load all the faces (uncomment to load a group)
    load_faces("BTS")
    # load_faces("ITZY")

    print("Enter ` key to run facial recognition and 1 to quit ")
    while True:
        a = keyboard.read_key()

        if a == "1":
            break
        elif a == "`":
            if not known_faces:
                print("No faces were loaded, check if load_faces has been called!")

            print("Screenshot taken!")
            ss = get_screenshot()
            # cur_group = input("Enter group to search: ")
            cur_group = "BTS"
            match_faces_ss(cur_group, ss)
