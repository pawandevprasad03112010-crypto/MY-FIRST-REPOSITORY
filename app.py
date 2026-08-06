from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# होम पेज (फ्रंटएंड) लोड करने के लिए
@app.route('/')
def index():
    return render_template('index.html')

# गूगल लॉगिन या यूजर लॉगिन को हैंडल करने के लिए API
@app.route('/api/login', methods=['POST'])
def login():
    # यहाँ आप ऑथेंटिकेशन या डेटाबेस लॉजिक लिख सकते हैं
    return jsonify({
        "status": "success",
        "message": "Login Successful"
    })

# वोटिंग को प्रोसेस करने के लिए API
@app.route('/api/vote', methods=['POST'])
def vote():
    data = request.get_json()
    contestant_name = data.get('contestant', 'Unknown')
    
    # यहाँ वोट डेटाबेस में सेव करने का लॉजिक आएगा
    print(f"Vote received for: {contestant_name}")
    
    return jsonify({
        "status": "success",
        "message": f"VOTE SUCCESSFUL for {contestant_name}"
    })

if __name__ == '__main__':
    app.run(debug=True)
  
