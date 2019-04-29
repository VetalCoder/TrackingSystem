import tkinter
import cv2
import PIL.Image
import PIL.ImageTk
import datetime
# import numpy as np
import skimage.measure


class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.photo = None

        # open video source (by default this will try to open the computer web cam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        # Button that starts tracking
        self.btn_track_start = tkinter.Button(window, text="Start tracking", width=50, command=self.track_start)
        self.btn_track_start.pack(anchor=tkinter.CENTER, expand=True)

        # Button that stops tracking
        self.btn_track_stop = tkinter.Button(window, text="Stop tracking", width=50, command=self.track_stop)
        self.btn_track_stop.pack(anchor=tkinter.CENTER, expand=True)

        # Labes that shows writing
        self.show_label = tkinter.Canvas(window, width=27, height=27, background='white')
        self.show_label.place(x=10, y=10)
        self.bool_show = False

        # tracking flag
        self.track = 0   # 0

        # video
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = None
        self.counts_after = 0
        self.CADRES_AFTER_MOVING = 40

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10
        self.update()

        self.window.mainloop()

    def show_write_label(self):
        self.show_label.create_oval(1, 1, 26, 26, fill='red', tags="oval")

    def hide_write_label(self):
        self.show_label.delete("oval")

    def track_start(self):
        # set default
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite("default.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        self.track = 1

    def track_stop(self):
        self.track = 0

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

        # detecting moves
        if self.counts_after:
            self.counts_after -= 1
        if self.track == 1:
            if self.compare_mse(cv2.imread("default.jpg"), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)) > 45:  # accuracy(30)
                self.counts_after = self.CADRES_AFTER_MOVING  # cadres after false
                cv2.imwrite("default.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        self.start_writing_video(self.counts_after, frame)

        self.window.after(self.delay, self.update)

    def start_writing_video(self, counts, frame):

        if not self.video_writer and counts == self.CADRES_AFTER_MOVING:
            time_ = datetime.datetime.now()
            name_ = "Video {}.avi".format(time_.isoformat(" "))
            self.video_writer = cv2.VideoWriter(name_, self.fourcc, 20, (640, 480))
            self.show_write_label()

        if counts > 0:
            # frame = cv2.flip(frame, 0)
            self.video_writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        else:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
                self.hide_write_label()

    @staticmethod
    def compare_mse(first_im, sec_im):
        return skimage.measure.compare_mse(first_im, sec_im)

    @staticmethod
    def compare_ssim(first_im, sec_im):
        return skimage.measure.compare_ssim(first_im, sec_im, multichannel=True)

    @staticmethod
    def compare_nrmse(first_im, sec_im):
        return skimage.measure.compare_nrmse(first_im, sec_im)


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return None

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")
