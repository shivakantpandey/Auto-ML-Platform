from flask import Flask,request,redirect,url_for,session,flash,render_template
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename   # secured file upload
from datetime import datetime
import database
import model

app=Flask(__name__)
app.secret_key='QwErTY9934@123'
@app.route('/')
def HomePage():
	return render_template('index.html')
@app.route('/register')
def register():
	return render_template('register.html')	
@app.route('/login')
def login():
	return render_template('login.html')
@app.route('/aboutus')
def aboutus():
	return render_template('aboutus.html')
@app.route('/analytics_portal')
def analytics_portal():
	return render_template('corp_portal.html')
@app.route('/admin')
def admin():
	return render_template('admin.html')
@app.route('/settings')
def settings():
	return render_template('settings.html')
@app.route('/registerBack',methods=['POST'])
def registerBack():
	registrar=database.Registration()
	if request.method=='POST':
		userId=request.form['userId']
		password=sha256_crypt.encrypt(request.form['password'])
		email=request.form['email']
		profilePic=request.files['profilePic']
		fileName=userId + secure_filename(profilePic.filename)
		profilePic.save('static/PROFILE_PIC/'+fileName)
	else:
		flash("Unsupported method of registration! Please use the registration tab instead.",'alert alert-danger')
		return redirect(url_for("HomePage"))
	profilePath='static/PROFILE_PIC/'+fileName
	res=registrar.registerUser(userId,password,email,profilePath)
	print(res)
	if res==True:
		# as we advance, incorporate functionality of OTP verification as well.
		flash("You are successfully registered! verification link has been sent to your registered E-mail.",'alert alert-success') 
		return redirect(url_for('login'))
	else:
		flash("User with provided data already exists! ",'alert alert-danger')
		return redirect(url_for('register'))

@app.route('/loginBack',methods=['POST'])
def loginBack():
	authenticator=database.AuthLogin()
	if request.method=='POST':
		userId=request.form['userId']
		password=request.form['password']
	else:
		flash("Unsupported method of login! Please use the login tab instead.",'alert alert-danger')
		return redirect(url_for("HomePage"))
	status,res,msg,category=authenticator.checkCredentials(userId,password)
	flash(msg,category)
	if status==True:
		session['username']=res[0][0]
		session['email']=res[0][2]
		session['profilePic']=res[0][3]
		session['type']=res[0][6]
		session['userId']=res[0][4]
		return redirect(url_for('HomePage'))
	else:
		return redirect(url_for('login'))

@app.route('/logout')
def logout():
	flash('You are successfully logged out!','alert alert-success')
	session.pop('username',None)
	session.pop('email',None)
	session.pop('profilePic',None)
	session.pop('type',None)
	session.pop('userId',None)
	return redirect(url_for('HomePage'))

@app.route('/activate')
def activate():
	otp = request.args.get('otp')
	userId=request.args.get('userId')
	otpVal=database.otpValidator()
	if otpVal.validate(otp,userId)==True:
		flash("Congratulations! Your account has been activated. Try logging in.",'alert alert-success')
		return redirect(url_for('login'))
	else:
		flash("OTP verification Failed! Try again later.",'alert alert-danger')
		return redirect(url_for('HomePage'))

@app.route('/user_fetch',methods=['GET'])
def user_fetch():
	if request.method=='GET':
		user_data_fetcher=database.user_data()
		res=user_data_fetcher.getUserData()
		response=''
		response+='<br><table>'
		response+='<tr>'
		response+='<th>User Id</th>'
		response+='<th>User Name</th>'
		response+='<th>User Mail</th>'
		response+='<th>User Profile picture</th>'
		response+='<th>Action</th>'
		response+='</tr>'
		if len(res)!=0:
			for i in res:
				response+=f"<tr><td>{i[0]}</td><td>{i[1]}</td><td>{i[2]}</td>"
				response+='<td><img src="'+str(i[3])+'" class="profile"></td>'
				if int(i[4])==1:
					response+='<td><input type="submit" class="deactivate" value="Deactivate" onClick="deactivate('+str(i[0])+')"></td></tr>'
				else:
					response+='<td><input type="submit" class="activate" value="Activate" onClick="activate('+str(i[0])+')"></td></tr>'
		return response
			
@app.route('/activate_user',methods=['GET'])
def activate_user():
	if request.method=='GET':	
		uid=request.args.get('userId')
		act_handler=database.activation_handler()
		stat=act_handler.activate(uid)
		#if stat:
		#	flash("Congratulations! the user has been activated.",'alert alert-success')
		#else:
		#	flash("Faced some issue while updaing the status",'alert alert-danger')	
	
@app.route('/deactivate_user',methods=['GET'])
def deactivate_user():
	if request.method=='GET':
		uid=request.args.get('userId')
		act_handler=database.activation_handler()
		stat=act_handler.deactivate(uid)
		#if stat:
		#	flash("Congratulations! the user has been deactivated.",'alert alert-success')
		#else:
		#	flash("Faced some issue while updaing the status",'alert alert-danger')	

@app.route('/change_credit',methods=['GET'])
def change_credit():
	if request.method=='GET':
		val=request.args.get("value")
		mode=request.args.get("mode")
		userId=session['userId']
		if mode=="1":
			# change password.
			registrar=database.Registration()
			registrar.updateProfile(sha256_crypt.encrypt(val),mode,userId)

		elif mode=="2":
			# change username.
			registrar=database.Registration()
			registrar.updateProfile(val,mode,userId)
			
@app.route('/changeProfPic',methods=['POST'])
def changeProfPic():
	if request.method=='POST':
		# change profile pic.
		profilePic=request.files['profpic']	
		fileName=session['profilePic']
		profilePic.save(fileName)
		return redirect(url_for('HomePage'))

@app.route('/analyse',methods=['POST'])
def analyse():
	if request.method=='POST':
		plot_mode=request.form['plots']
		model_mode=request.form['model']
		denoise_mode=request.form['denoise']
		dataset=request.files['dataset']
		fileName=session["username"]+ str(int(model.time())) + secure_filename(dataset.filename)
		dataset.save('dataset/'+fileName)
		session["dataset"]='dataset/'+fileName
		session["denoise"]=denoise_mode
		session["model"]=model_mode
		result=""
		analytics_engine=model.Analytics('dataset/'+fileName,int(denoise_mode))  # denoise_mode=2 ; means it will drop the NAN rows.
		plot_loc_list=analytics_engine.get_plot(session["username"]+ str(int(model.time())),int(plot_mode))
		result+="<center><h1>Pre-Modelling Plots (Top 100 records)</h1><br>"
		result+="<table>"
		i=0
		while(i<len(plot_loc_list)):
			result+="<tr>"
			if(i<len(plot_loc_list)):
				result+='<td><img class="pre_model_plot" src="'+plot_loc_list[i]+'"></td>'
				i+=1
			if(i<len(plot_loc_list)):
				result+='<td><img class="pre_model_plot" src="'+plot_loc_list[i]+'"></td>'
				i+=1
			result+="</tr>"
		result+="</table><br><br>"
		result+="<h1>Metadata Information (after denoising)</h1><br>"
		result+=analytics_engine.get_metadata_info()
		result+="<br><br>"
		result+="<h1>Statistical Information (after denoising)</h1><br>"
		result+=analytics_engine.get_stats_info()
		result+="<br><br>"
		result+="<h1>Select column(s) which needs to be present as predictor set</h1><br>"
		data_columns=analytics_engine.get_data_columns()
		result+='<form method="post" action="predict"><table>'
		for col in data_columns:
			result+='<tr><td><input type="checkbox" id="predictor" name="predictor" value="'+ str(col) +'"></td>'
			result+='<td><label for="predictor">'+ str(col) +'</label></td></tr>'
		result+="</table><br><br>"
		result+="<h1>Select column(s) which needs to be present as target set</h1><br>"
		result+='<table>'
		for col in data_columns:
			result+='<tr><td><input type="checkbox" id="target" name="target" value="'+ str(col) +'"></td>'
			result+='<td><label for="target">'+ str(col) +'</label></td></tr>'
		result+='<tr><td><input type="submit" value="Train" class="activate"></td><td><input type="reset" value="reset" class="deactivate"></td></tr></table></form></center>'
		return render_template('report.html',report=result)
	else:
		print("GET!")
@app.route('/predict',methods=['POST'])
def predict():
	if request.method=='POST':
		analytics_engine=model.Analytics(session["dataset"],int(session["denoise"]))
		data_columns=analytics_engine.get_data_columns()
		result=""
		predictor_cols=request.form.getlist('predictor')
		target_cols=request.form.getlist('target')
		analytics_engine.preprocess(predictor_cols,target_cols)
		result=analytics_engine.model(session["username"]+ str(int(model.time())),session["model"])
		res=""
		res+="<center><table>"
		res+="<tr><td>R^2 Score : </td><td>"+ str(result["R2_score"]) +"</td></tr>"
		res+='<tr><td>Prediction visual : </td><td><img class="post_model_plot" src="'+ str(result["Model_Plot"]) +'"</td></tr>'
		res+="</table><center>"
		return render_template('report.html',report=res)

		


