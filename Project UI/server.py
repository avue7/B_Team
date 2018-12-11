from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def index():

	return render_template('index.html')

@app.route("/email",methods=['Post'])
def input():

	email = request.form['email']
	return 'Email is: %s <br/> <a href="/">Return</a>' % (email)

@app.route("/phpemail")
def phpinput():

	email = request.args.get('email','phpemail')
	return render_template('index.html',user=email,data=data) 

if __name__ == "__main__":
    app.run(debug='True')
