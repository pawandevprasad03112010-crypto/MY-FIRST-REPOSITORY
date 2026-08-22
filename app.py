from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>WhatsApp Bulk Sender</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; padding: 20px; }
        .container { max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); margin: auto; }
        textarea { width: 100%; height: 150px; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #25D366; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #1ebe5d; }
        .link-list { margin-top: 20px; }
        .link-item { display: block; background: #e0f7fa; padding: 8px; margin-bottom: 5px; text-decoration: none; color: #00796b; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>WhatsApp Bulk Link Generator</h2>
        <form method="POST">
            <label>मोबाइल नंबर (हर लाइन में एक, देश कोड के साथ जैसे 919876543210):</label>
            <textarea name="numbers" placeholder="919111111111\n919222222222">{{ numbers or '' }}</textarea>
            
            <label>भेजे जाने वाला मैसेज:</label>
            <textarea name="message" style="height: 100px;" placeholder="यहाँ अपना मैसेज लिखें...">{{ message or '' }}</textarea>
            
            <button type="submit">WhatsApp लिंक जनरेट करें</button>
        </form>

        {% if links %}
        <div class="link-list">
            <h3>आपके WhatsApp लिंक्स (Click करके भेजें):</h3>
            {% for num, link in links %}
                <a class="link-item" href="{{ link }}" target="_blank">संदेश भेजें: {{ num }}</a>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    links = []
    numbers_text = ""
    message = ""
    
    if request.method == 'POST':
        numbers_text = request.form.get('numbers', '')
        message = request.form.get('message', '')
        
        # नंबरों को लाइन-बाय-लाइन अलग करना
        raw_numbers = numbers_text.splitlines()
        for num in raw_numbers:
            clean_num = ''.join(filter(str.isdigit, num))
            if clean_num:
                # WhatsApp wa.me लिंक बनाना
                import urllib.parse
                encoded_msg = urllib.parse.quote(message)
                wa_link = f"https://wa.me/{clean_num}?text={encoded_msg}"
                links.append((clean_num, wa_link))
                
    return render_template_string(HTML_PAGE, links=links, numbers=numbers_text, message=message)

if __name__ == '__main__':
    app.run(debug=True)
    
