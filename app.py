from flask import Flask, render_template, send_file
import hashlib
import qrcode
from PIL import Image

app = Flask(__name__)

class Food:
    def __init__(self, name, variety, farm, size, production_date, expiry_date):
        self.name = name
        self.variety = variety
        self.farm = farm
        self.size = size
        self.production_date = production_date
        self.expiry_date = expiry_date
        self.info = name + ";" + variety + ";" + farm + ";" + size + ";" + production_date + ";" + expiry_date

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr')
def generate_qr():
    food_item = Food("milk", "whole milk 3.5% fat", "BOYDELLS DAIRY FARM", "1 lt", "2020-07-13", "2020-08-3")
    block_info = food_item.info + ";" + hashlib.sha256(food_item.info.encode()).hexdigest()

    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_code.add_data(block_info)
    qr_code.make(fit=True)

    img = qr_code.make_image(fill_color="black", back_color="white")
    img.save("static/qrcode_milk.png")

    return send_file("static/qrcode_milk.png", mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
