import glob

import cv2
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip  # planning to do more than just this with moviepy later :)

from helpers import frame_to_time

# which pixels are we trying to detect the color range of
DEATH_TEXT_PIXELS = [
    (149, 896),
    (332, 898),
    (79, 897),
]
# @TODO: define some pixels which should NOT be red to make it more reliable/lava-proof?

# what's the RGB color range we want to detect
DEATH_TEXT_RGB_RANGE = ([110, 0, 0], [166, 44, 44])

DETECT_FRAME_RANGE = 60  # how many frames do we skip each time


def main():
    vods = glob.glob('/home/teunb/nugivods/*.mp4')
    vods.sort()

    death_counter = 0
    for vod in vods:
        vidcap = cv2.VideoCapture(vod)

        success, image = vidcap.read()
        frame = 0  # what frame we're on right now
        not_dead_detect_frames = 0  # how many detect_frame ranges are we not dead for
        while success:
            if frame % DETECT_FRAME_RANGE == 0:
                image = vidcap.retrieve()[1]  # this actually does processing over the frame we cap, relatively slow
                if frame % 3600 == 0:
                    # log each minute
                    print(f'[{vod}] Currently @{frame_to_time(frame)}')

                lower, upper = DEATH_TEXT_RGB_RANGE
                # for some reason we need to revert the RGB range here
                lower = np.array(lower[::-1], dtype='uint8')
                upper = np.array(upper[::-1], dtype='uint8')
                # this creates a 2D array that sets all pixels that are within the color range to 255
                mask = cv2.inRange(image, lower, upper)

                # count amount of detection pixels that match the color range
                pixels_detected = 0
                for x, y in DEATH_TEXT_PIXELS:
                    if mask[y, x] == 255:
                        pixels_detected += 1

                # we can miss two detection pixels
                if pixels_detected >= len(DEATH_TEXT_PIXELS) - 1:
                    if not_dead_detect_frames > 5:
                        # if we weren't dead for 5 ranges, and we are now: CLIP THAT
                        death_counter += 1

                        # we clip the detection time with a 5 second range on both sides
                        start_second = int(frame / DETECT_FRAME_RANGE) - 5
                        end_second = int(frame / DETECT_FRAME_RANGE) + 5
                        ffmpeg_extract_subclip(vod, start_second, end_second, targetname=f'clips/{death_counter}.mp4')

                        # also write a framecap for debugging purposes
                        cv2.imwrite(f'frames/{death_counter}.jpg', image)

                    not_dead_detect_frames = 0
                    print(f'DEATH @{frame_to_time(frame)}')
                else:
                    not_dead_detect_frames += 1

            success = vidcap.grab()  # this just grabs the frame but doesn't do a lot of processing, so it's faster, I think...
            frame += 1


if __name__ == '__main__':
    main()
