from flask import Flask, render_template, request,session,redirect,url_for
app = Flask(__name__)
app.secret_key = 'Lahari@1214'
@app.route('/')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)