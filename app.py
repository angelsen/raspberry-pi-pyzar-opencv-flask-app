from flask import Flask, Response, render_template
from picamera2 import Camera
import cv2
from pyzbar.pyzbar import decode

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def gen_frames():
        camera = Camera()
        camera.start_streaming()

        while True:
            # Retrieve the current frame
            stream = camera.get_latest_stream()
            frame = stream.get_frame()

            # Convert the frame to RGB format
            frame = frame.convert('RGB')

            # Decode barcodes in the frame
            for d in decode(frame):
                s = d.data.decode()
                print(s)

                # Draw a rectangle around the barcode
                cv2.rectangle(frame, (d.rect.left, d.rect.top),
                                    (d.rect.left + d.rect.width, d.rect.top + d.rect.height), (0, 255, 0), 3)

                # Write the barcode data on the frame
                cv2.putText(frame, s, (d.rect.left, d.rect.top + d.rect.height), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)

            # Encode the modified frame as JPEG
            encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()

            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame + b'\r\n\r\n'

        #camera.stop_streaming()

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)