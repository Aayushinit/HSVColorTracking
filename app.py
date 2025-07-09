from flask import Flask, render_template, Response, request
import cv2
import numpy as np

app = Flask(__name__)

# Initialize the video capture
cap = cv2.VideoCapture(0)

# Default HSV values
l_h, l_s, l_v = 0, 0, 0
u_h, u_s, u_v = 255, 255, 255

def generate_frames():
    global l_h, l_s, l_v, u_h, u_s, u_v
    while True:
        success, frame = cap.read()
        if not success:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        l_b = np.array([l_h, l_s, l_v])
        u_b = np.array([u_h, u_s, u_v])

        mask = cv2.inRange(hsv, l_b, u_b)
        res = cv2.bitwise_and(frame, frame, mask=mask)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', res)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_hsv', methods=['POST'])
def set_hsv():
    global l_h, l_s, l_v, u_h, u_s, u_v
    l_h = int(request.form.get('l_h', 0))
    l_s = int(request.form.get('l_s', 0))
    l_v = int(request.form.get('l_v', 0))
    u_h = int(request.form.get('u_h', 255))
    u_s = int(request.form.get('u_s', 255))
    u_v = int(request.form.get('u_v', 255))
    return ('', 204)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

    # Release the video capture when the app is stopped
    cap.release()
