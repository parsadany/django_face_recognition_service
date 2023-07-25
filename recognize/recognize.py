import PIL.Image
from PIL import ImageFile
import requests
from io import BytesIO
import dlib
import numpy as np

# -*- coding: utf-8 -*-

__author__ = """parsadany"""
__email__ = 'parsadany@gmail.com'
__version__ = '0.1.0'

from pkg_resources import resource_filename

class LearnedModels:
    @staticmethod
    def pose_predictor_model_location():
        return resource_filename(__name__, "learned_data/shape_predictor_68_face_landmarks.dat")

    @staticmethod
    def pose_predictor_five_point_model_location():
        return resource_filename(__name__, "learned_data/shape_predictor_5_face_landmarks.dat")

    @staticmethod
    def face_recognition_model_location():
        return resource_filename(__name__, "learned_data/dlib_face_recognition_resnet_model_v1.dat")

    @staticmethod
    def cnn_face_detector_model_location():
        return resource_filename(__name__, "learned_data/mmod_human_face_detector.dat")



class FaceRecognize:
    
    def __init__(self) -> None:
        
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        self.face_detector = dlib.get_frontal_face_detector()

        predictor_68_point_model = LearnedModels.pose_predictor_model_location()
        self.pose_predictor_68_point = dlib.shape_predictor(predictor_68_point_model)
        
        predictor_5_point_model = LearnedModels.pose_predictor_five_point_model_location()
        self.pose_predictor_5_point = dlib.shape_predictor(predictor_5_point_model)
        
        cnn_face_detection_model = LearnedModels.cnn_face_detector_model_location()
        self.cnn_face_detector = dlib.cnn_face_detection_model_v1(cnn_face_detection_model)
        
        face_recognition_model = LearnedModels.face_recognition_model_location()
        self.face_encoder = dlib.face_recognition_model_v1(face_recognition_model)


    def _rect_to_css(self, rect):
        """
        Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order

        :param rect: a dlib 'rect' object
        :return: a plain tuple representation of the rect in (top, right, bottom, left) order
        """
        return rect.top(), rect.right(), rect.bottom(), rect.left()


    def _css_to_rect(self, css):
        """
        Convert a tuple in (top, right, bottom, left) order to a dlib `rect` object

        :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
        :return: a dlib `rect` object
        """
        return dlib.rectangle(css[3], css[0], css[1], css[2])


    def _trim_css_to_bounds(self, css, image_shape):
        """
        Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.

        :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
        :param image_shape: numpy shape of the image array
        :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
        """
        return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)



    def load_image_url(self, url, mode='RGB'):
        """
        Loads an image url (.jpg, .png, etc) into a numpy array

        :param file: image url string to load
        :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
        :return: image contents as numpy array
        """
        response = requests.get(url)
        img = PIL.Image.open(BytesIO(response.content))
        if mode:
            img = img.convert(mode)
        return np.array(img)

    def get_matching_id_encodings(self, matching_id):
        from recognize.models import Profile, KnownImage
        images = KnownImage.objects.filter(profile=Profile.objects.get(matching_id=matching_id))
        # print(images)
        return [self.get_img_encodings(self.load_image_url(url=image.url)) for image in images]

    def get_img_encodings(self, img):
        faces = self.face_encodings(img)
        return faces

    def get_img_encodings(self, face_image, known_face_locations=None, num_jitters=1, model="small"):
        """
        Given an image, return the 128-dimension face encoding for each face in the image.

        :param face_image: The image that contains one or more faces
        :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
        :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
        :param model: Optional - which model to use. "large" (default) or "small" which only returns 5 points but is faster.
        :return: A list of 128-dimensional face encodings (one for each face in the image)
        """
        raw_landmarks = self._raw_face_landmarks(face_image, known_face_locations, model)
        return [np.array(self.face_encoder.compute_face_descriptor(face_image, raw_landmark_set, num_jitters)) for raw_landmark_set in raw_landmarks]


    def face_distance(self, face_encodings, face_to_compare):
        """
        Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
        for each comparison face. The distance tells you how similar the faces are.

        :param faces: List of face encodings to compare
        :param face_to_compare: A face encoding to compare against
        :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
        """
        if len(face_encodings) == 0:
            return np.empty((0))

        return np.linalg.norm(face_encodings - face_to_compare, axis=1)


    def load_image_file(self, file, mode='RGB'):
        """
        Loads an image file (.jpg, .png, etc) into a numpy array

        :param file: image file name or file object to load
        :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
        :return: image contents as numpy array
        """
        im = PIL.Image.open(file)
        if mode:
            im = im.convert(mode)
        return np.array(im)


    def _raw_face_locations(self, img, number_of_times_to_upsample=1, model="hog"):
        """
        Returns an array of bounding boxes of human faces in a image

        :param img: An image (as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                      deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
        :return: A list of dlib 'rect' objects of found face locations
        """
        if model == "cnn":
            return self.cnn_face_detector(img, number_of_times_to_upsample)
        else:
            return self.face_detector(img, number_of_times_to_upsample)


    def face_locations(self, img, number_of_times_to_upsample=1, model="hog"):
        """
        Returns an array of bounding boxes of human faces in a image

        :param img: An image (as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                      deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
        :return: A list of tuples of found face locations in css (top, right, bottom, left) order
        """
        if model == "cnn":
            return [self._trim_css_to_bounds(self._rect_to_css(face.rect), img.shape) for face in self._raw_face_locations(img, number_of_times_to_upsample, "cnn")]
        else:
            return [self._trim_css_to_bounds(self._rect_to_css(face), img.shape) for face in self._raw_face_locations(img, number_of_times_to_upsample, model)]


    def _raw_face_locations_batched(self, images, number_of_times_to_upsample=1, batch_size=128):
        """
        Returns an 2d array of dlib rects of human faces in a image using the cnn face detector

        :param img: A list of images (each as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :return: A list of dlib 'rect' objects of found face locations
        """
        return self.cnn_face_detector(images, number_of_times_to_upsample, batch_size=batch_size)


    def batch_face_locations(self, images, number_of_times_to_upsample=1, batch_size=128):
        """
        Returns an 2d array of bounding boxes of human faces in a image using the cnn face detector
        If you are using a GPU, this can give you much faster results since the GPU
        can process batches of images at once. If you aren't using a GPU, you don't need this function.

        :param images: A list of images (each as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :param batch_size: How many images to include in each GPU processing batch.
        :return: A list of tuples of found face locations in css (top, right, bottom, left) order
        """
        def convert_cnn_detections_to_css(self, detections):
            return [self._trim_css_to_bounds(self._rect_to_css(face.rect), images[0].shape) for face in detections]

        raw_detections_batched = self._raw_face_locations_batched(images, number_of_times_to_upsample, batch_size)

        return list(map(convert_cnn_detections_to_css, raw_detections_batched))


    def _raw_face_landmarks(self, face_image, face_locations=None, model="large"):
        if face_locations is None:
            face_locations = self._raw_face_locations(face_image)
        else:
            face_locations = [self._css_to_rect(face_location) for face_location in face_locations]

        pose_predictor = self.pose_predictor_68_point

        if model == "small":
            pose_predictor = self.pose_predictor_5_point

        return [pose_predictor(face_image, face_location) for face_location in face_locations]


    def face_landmarks(self, face_image, face_locations=None, model="large"):
        """
        Given an image, returns a dict of face feature locations (eyes, nose, etc) for each face in the image

        :param face_image: image to search
        :param face_locations: Optionally provide a list of face locations to check.
        :param model: Optional - which model to use. "large" (default) or "small" which only returns 5 points but is faster.
        :return: A list of dicts of face feature locations (eyes, nose, etc)
        """
        landmarks = self._raw_face_landmarks(face_image, face_locations, model)
        landmarks_as_tuples = [[(p.x, p.y) for p in landmark.parts()] for landmark in landmarks]

        # For a definition of each point index, see https://cdn-images-1.medium.com/max/1600/1*AbEg31EgkbXSQehuNJBlWg.png
        if model == 'large':
            return [{
                "chin": points[0:17],
                "left_eyebrow": points[17:22],
                "right_eyebrow": points[22:27],
                "nose_bridge": points[27:31],
                "nose_tip": points[31:36],
                "left_eye": points[36:42],
                "right_eye": points[42:48],
                "top_lip": points[48:55] + [points[64]] + [points[63]] + [points[62]] + [points[61]] + [points[60]],
                "bottom_lip": points[54:60] + [points[48]] + [points[60]] + [points[67]] + [points[66]] + [points[65]] + [points[64]]
            } for points in landmarks_as_tuples]
        elif model == 'small':
            return [{
                "nose_tip": [points[4]],
                "left_eye": points[2:4],
                "right_eye": points[0:2],
            } for points in landmarks_as_tuples]
        else:
            raise ValueError("Invalid landmarks model type. Supported models are ['small', 'large'].")


    def face_encodings(self, face_image, known_face_locations=None, num_jitters=1, model="small"):
        """
        Given an image, return the 128-dimension face encoding for each face in the image.

        :param face_image: The image that contains one or more faces
        :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
        :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
        :param model: Optional - which model to use. "large" (default) or "small" which only returns 5 points but is faster.
        :return: A list of 128-dimensional face encodings (one for each face in the image)
        """
        raw_landmarks = self._raw_face_landmarks(face_image, known_face_locations, model)
        return [np.array(self.face_encoder.compute_face_descriptor(face_image, raw_landmark_set, num_jitters)) for raw_landmark_set in raw_landmarks]


    def compare_faces(self, known_face_encodings, face_encoding_to_check, tolerance=0.6):
        """
        Compare a list of face encodings against a candidate encoding to see if they match.

        :param known_face_encodings: A list of known face encodings
        :param face_encoding_to_check: A single face encoding to compare against the list
        :param tolerance: How much distance between faces to consider it a match. Lower is more strict. 0.6 is typical best performance.
        :return: A list of True/False values indicating which known_face_encodings match the face encoding to check
        """
        return list(self.face_distance(known_face_encodings, face_encoding_to_check) <= tolerance)


    def match_faces_from_url(self, url, matching_id, mode='RGB'):
        """
        Gets the url of image, and the person matching_id to check that it matches or not! 

        :param url: image file name or file object to load
        :param matching_id: matching id of a a person that should be checked. Anyone known by the app has a matching_id.
        :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
        :return: dict {
            "face_count": Number of faces in picture, 
            "is_matched": Matched or not! (bool), 
            "results": Matched Positions Data (list) 
                [
                    {
                        "known_encodings": __,
                        "known_id": __,
                        "dictances": [numbers...],
                        "face_location": location,
                        "matched_locations": [locations...]
                    },
                    ...
                ]
            }
        """
        known_encodings = self.get_matching_id_encodings(matching_id)
        unknown_img = self.load_image_url(url)
        unknown_encodings = self.get_img_encodings(unknown_img)
        results = []
        matched = False
        matched_position = []
        response = {
            "face_count": len(unknown_encodings),
            "is_matched": False,
            "results": []
        }
        # print(known_encodings, unknown_encodings)
        for unknown_encoding in unknown_encodings:
            for i in range(len(known_encodings)):
                result = self.compare_faces(known_encodings[i], unknown_encoding) 
                # print(result)
                distances = self.face_distance(known_encodings, unknown_encoding)
                if True in result:
                    response["is_matched"] = True
                    results.append(
                        {
                            "known_encodings": known_encodings,
                            "known_id": "__",
                            "dictances": distances,
                            "face_location": "",
                            "matched_locations": []
                        }
                    )
        response["results"] = results
        return response
            

    


        