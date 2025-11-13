import numpy as np
from PIL import Image, ImageFont, ImageDraw
import cv2

class DicomOverlay:
    '''
    An object of this class can be given text configurations
    Further, the object can be used to annotate multiple images with any text
    '''
    def __init__(self, text_config=dict()):
        '''
        Sets text configurations
        '''
        self.text_config = text_config

        if 'font' not in self.text_config:
            self.text_config['font'] = "arial.ttf"

        if 'fill' not in self.text_config:
            self.text_config['fill'] = 'white'

        if 'title align' not in self.text_config:
            self.text_config['title align'] = 'center'


    def draw_annotation(self, image, position, text):
        '''
        Writes text and draws box around it
        Input: image, top left and bottom right coordinates of textbox, text to write
        Output: text annotated image
        '''

        text_mask = np.zeros((image.shape[0],image.shape[1]))
        # pil_image = Image.fromarray(image)
        pil_image = Image.fromarray(text_mask)

        draw = ImageDraw.Draw(pil_image)
        font_size = 12
        font = ImageFont.truetype(self.text_config['font'], font_size)
        spacing = int(font_size//3)   

        ## Draw title
        
        title_font = ImageFont.truetype( self.text_config['font'], font_size)
        print(position,text,title_font)
        draw.text(position, text,
                  font=title_font,
                  fill=self.text_config['fill'],
                  spacing=spacing,
                  align=self.text_config['title align'])
       


        # Drawing box around it
        text_image = np.array(pil_image)
        py,px = np.where(text_image)
        
        top_left = [np.min(px),np.min(py)]
        bottom_right = [np.max(px),np.max(py)]

        pad = 20
        top_left = (top_left[0]-pad,top_left[1]-pad)
        bottom_right = (bottom_right[0]+pad,bottom_right[1]+pad)

        start = top_left
        end = bottom_right
        
        color = (255, 255, 255)
        
        cv2.rectangle(text_image, start, end, color=color, thickness=int(image.shape[0]//500))
        return text_image
