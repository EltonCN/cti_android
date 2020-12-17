import urllib.request
from urllib.error import URLError
import json
import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
import sys
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
import cv2 as cv

from sensor_msgs.msg import Image, CompressedImage, CameraInfo

class CameraReceiver(Node):
    '''!
        Receptor e publicador de imagens recebidas via rede de uma camera de celular
    '''

    def __init__(self):
        super().__init__('camera_receiver')
        self.pubImg = self.create_publisher(Image, "image_raw/image", 10)
        self.pubImgCompress = self.create_publisher(CompressedImage, "image_raw/compressed", 10)

        self.declare_parameter("ip","192.168.2.101")
        self.declare_parameter("frame_id","cellphone_camera")

        ip = self.get_parameter("ip").get_parameter_value().string_value

        self.cap = cv.VideoCapture("http://"+ip+":8080/video")

        self.callbackGroup = ReentrantCallbackGroup()

        timer_period = 0.016666  # segundos
        self.timer = self.create_timer(timer_period, self.timerCallback)#, callback_group=self.callbackGroup)

    def timerCallback(self):
        '''!
            Callback do timer que recebe a imagem e publica
        '''
        
        ret, frame = self.cap.read()

        frameId = self.get_parameter("frame_id").get_parameter_value().string_value

        tempo1 = cv.getTickCount()

        if(ret):

            imgMsg = Image()

            data = frame.flatten().tolist()

            imgMsg._data = data

            imgMsg.height = frame.shape[0]
            imgMsg.width = frame.shape[1]

            imgMsg.encoding = "8UC3"
            imgMsg.is_bigendian = 0
            imgMsg.step = imgMsg.width*3

            time = self.get_clock().now().to_msg()
            imgMsg.header.stamp = time
            
            imgMsg.header.frame_id = frameId
            
            self.pubImg.publish(imgMsg)

            #compImgMsg = bridge.cv2_to_compressed_imgmsg(frame)
            #compImgMsg.header.stamp = time
            #compImgMsg.header.frame_id = frameId
            #self.pubImgCompress.publish(compImgMsg)

            self.publishInfo(imgMsg.header)

        tempo2 = cv.getTickCount()


    def publishInfo(self, header):
        '''!
            @todo Implementar publicacao de CameraInfo
        '''
        pass
        

def main(args=None):
    rclpy.init(args=args)

    node = CameraReceiver()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)

    #executor.spin()

    rclpy.spin(node)

    node.destroy_node()
    executor.shutdown()
    rclpy.shutdown()



if __name__ == '__main__':
    main()
                
