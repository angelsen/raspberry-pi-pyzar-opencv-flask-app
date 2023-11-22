from flask import Flask, Response, render_template
import cv2
from pyzbar.pyzbar import decode
from picamera2 import Picamera2

app = Flask(__name__)
picam2 = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_camera')
def start_camera():
    global picam2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
    return '', 204

@app.route('/stop_camera')
def stop_camera():
    global picam2
    if picam2:
        picam2.stop()
        picam2 = None
    return '', 204

@app.route('/video_feed')
def video_feed():
    
    def gen_frames():
        global picam2
        while True:
            if picam2:
                frame = picam2.capture_array()
                if frame is not None:
                    # Your barcode decoding and frame manipulation code here
                    for d in decode(frame):
                        s = d.data.decode()
                        print(s)
                        frame = cv2.rectangle(frame, (d.rect.left, d.rect.top),
                                              (d.rect.left + d.rect.width, d.rect.top + d.rect.height), (0, 255, 0), 3)
                        frame = cv2.putText(frame, s, (d.rect.left, d.rect.top + d.rect.height),
                                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)

                    encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame + b'\r\n\r\n'
                else:
                    print('Error capturing frame')
                    break
            else:
                break  # Exit the loop if the camera is not started

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)