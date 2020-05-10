from flask import Flask, render_template,Response, request, redirect, url_for
import emailClientReader
import sys

app = Flask(__name__)

@app.route('/')
def index():
        return render_template('index.html')


def add_rule():
    print("adding rule")

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print ("Test button pressed", file=sys.stderr)
    return ("nothing")

@app.route('/update_rules/', methods=["POST"])
def update_rules():
    pass       

@app.route('/add-audio')
def add_audio():
    return "WIP"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
