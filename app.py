from flask import Flask, render_template,Response, request, redirect, url_for
import emailClientReader

app = Flask(__name__)

@app.route('/')
def index():
        return render_template('index.html')

def update():
        pass

def add_rule():
        print("adding rule")


@app.route('/add-audio')
def add_audio():
        return "WIP"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
