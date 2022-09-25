from datetime import datetime
import os
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from flask import render_template, session, redirect, url_for, flash, abort, request, current_app
from . import main
from .forms import HeartInformationForm, EditProfileForm, EditProfileAdminForm, SearchBarForm
from .. import db
from ..models import User, Patient, Role
from flask_login import current_user, login_required
from ..static.make_prediction import predict_disease_proba
from ..decorators import admin_required


@main.route('/')
def index():
    welcome_pic = os.path.join('static', 'signal.jpg')
    return render_template('index.html',
                           welcome_pic=welcome_pic)

@main.route('/about')
def about():
    coefficients = os.path.join('static', 'coefficients.png')
    return render_template('about.html',
                           coefficients=coefficients)

@main.route('/predict', methods=['GET', 'POST'])
def predict():
    form = HeartInformationForm()  
    if form.validate_on_submit():      
        
        if (not (form.sex.data or form.cp.data or form.restecg.data or
                 form.slope.data or form.thal.data)) or ((form.fbs.data == "") 
                                                         or (form.exang.data == "")):
            flash('Incomplete form: please enter missing fields to continue.')
        else:
            model_input = [
                form.age.data,
                int(form.sex.data),
                int(form.cp.data),
                form.trestbps.data,
                form.chol.data,
                int(form.fbs.data),
                int(form.restecg.data),
                form.thalach.data,
                int(form.exang.data),
                form.oldpeak.data,
                int(form.slope.data),
                form.ca.data,
                int(form.thal.data)
                ]
            pred_proba = predict_disease_proba(model_input)
            
            img = BytesIO()
            x = ["Heart disease", "No heart disease"]
            height = [(1-pred_proba[0][0])*100, pred_proba[0][0]*100]
            bars = plt.bar(x=x, height=height, color = "#65aabb")
            plt.ylabel('Probability (%)')
            plt.ylim(0, 100)
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x()+.325, yval + .5, "{}%".format(round(yval,2)))
            plt.savefig(img, format='png')
            plt.close()
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode('utf8')
            
            if current_user.is_authenticated:
                
                temp = dict()
                if form.sex.data == "0":
                    temp["sex"] = "Female"
                else:
                    temp["sex"] = "Male"
                if form.cp.data == "1":
                    temp["cp"] = "Typical"
                elif form.cp.data == "2":
                    temp["cp"] = "Atypical"
                elif form.cp.data == "3":
                    temp["cp"] = "Non-anginal"
                else:
                    temp["cp"] = "Asymptomatic"
                if form.fbs.data == "0":
                    temp["fbs"] = False
                else:
                    temp["fbs"] = True
                if form.restecg.data == "0":
                    temp["restecg"] = "Normal"
                elif form.restecg.data == "1":
                    temp["restecg"] = "Abnormal"
                else:
                    temp["restecg"] = "Hypertropy"
                if form.exang.data == "0":
                    temp["exang"] = False
                else:
                    temp["exang"] = True
                if form.slope.data == "1":
                    temp["slope"] = "Upsloping"
                elif form.slope.data == "2":
                    temp["slope"] = "Flat"
                else:
                    temp["slope"] = "Downsloping"
                if form.thal.data == "0":
                    temp["thal"] = "No test result available"
                elif form.thal.data == "3":
                    temp["thal"] = "Normal"
                elif form.thal.data == "6":
                    temp["thal"] = "Fixed defect"
                else:
                    temp["thal"] = "Reversible defect"
                
                
                patient_information = Patient(doctor_id=current_user.username,
                                              submission_datetime=datetime.utcnow(),
                                              patient_name=form.patient_name.data,
                                              age=form.age.data,
                                              sex=temp["sex"],
                                              cp=temp["cp"],
                                              trestbps=form.trestbps.data,
                                              chol=form.chol.data,
                                              fbs=temp["fbs"],
                                              restecg=temp["restecg"],
                                              thalach=form.thalach.data,
                                              exang=temp["exang"],
                                              oldpeak=form.oldpeak.data,
                                              slope=temp["slope"],
                                              ca=form.ca.data,
                                              thal=temp["thal"],
                                              disease_proba=np.round(pred_proba[0][1]*100,2))
                db.session.add(patient_information)
                db.session.commit()
        
            else:
                pass
            
            return render_template('results.html',
                                   patient_name=form.patient_name.data,
                                   probability=pred_proba,
                                   plot_loc=plot_url)

    return render_template('predict.html',
                        form=form,
                        name=session.get('name'),
                        known=session.get('known', False))

@main.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = SearchBarForm()
    user = User.query.filter_by(username=username).first()    
    if user is None:
        abort(404)
    query = Patient.query
    page = request.args.get('page',1,type=int)
    if form.validate_on_submit():
        if form.name.data:
            pagination = query.filter_by(doctor_id=current_user.username).filter_by(patient_name=form.name.data).order_by(Patient.submission_datetime.desc()).paginate(
                page, per_page=current_app.config['HDP_PATIENTS_PER_PAGE'],
                error_out=False)
            patients = pagination.items
            return render_template('user.html', user=user, patients=patients, form=form, pagination=pagination)
        else:
            pagination = query.filter_by(doctor_id=current_user.username).order_by(Patient.submission_datetime.desc()).paginate(
                page, per_page=current_app.config['HDP_PATIENTS_PER_PAGE'],
                error_out=False)
            patients = pagination.items
            return render_template('user.html', user=user, patients=patients, form=form, pagination=pagination)                
    else:
        pagination = query.filter_by(doctor_id=current_user.username).order_by(Patient.submission_datetime.desc()).paginate(
                page, per_page=current_app.config['HDP_PATIENTS_PER_PAGE'],
                error_out=False)
        patients = pagination.items
        return render_template('user.html', user=user, patients=patients, form=form, pagination=pagination)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)