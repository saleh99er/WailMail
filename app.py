from flask import Flask, render_template,Response, request, redirect, url_for
import emailClientReader
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', update_msg="waiting for user input and update button press")


#def add_rule():
#    print("adding rule")


@app.route('/update', methods=["POST"])
def update_rules():
    update_msg = "Updating..."
    contain_str = request.form['str_field']

    #user_input = 'You entered: {}'.format(request.form)
    print(contain_str, file=sys.stderr)
    print(update_msg, file=sys.stderr)
    return 'contains: ' + contain_str

@app.route('/add-audio')
def add_audio():
    return "WIP"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
