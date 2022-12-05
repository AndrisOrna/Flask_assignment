from flask import Flask, render_template, url_for, request, redirect
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import io
import pickle
from PIL import Image
from base64 import b64encode
import cv2
import requests

import pandas as pd
import plotly.express as px
import plotly

import Dv4ddcPreproc

import foo
global cars
global flag

flag = 0
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db' # configuration for sql 3 flashes means fast, can use //// instead
db = SQLAlchemy(app)# hold Ctrl and click to see inside

@app.before_first_request
def create_tables():
    db.create_all()# if db file doesn't exist

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow) # column for date now
    def __repr__(self):
        return '<Car %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():  # going to the first webpage
    
    # cars = None
    # try:
    #     cars = Car.query.order_by(Car.date_created).all()
    #     for car in cars:
    #         # Download Image
    #         car.content = json.loads(car.content)

    #         if car.content.get('ImageURL') is not None:
    #             try:
    #                 ImageURL = car.content['ImageURL']
    #                 car.content['Image'] = foo.retrieve_image(ImageURL)
    #             except:
    #                 pass

    #         car.content = ImmutableMultiDict(car.content)
    # except:
    #     pass
    #     a = 1
    return render_template('index.html')


@app.route('/typein', methods = ['GET', 'POST']) # getting the webpage typein.html
def typein():

    if request.method == 'POST': 
        content = json.dumps(request.form) # This will lose the ImmutableMultiDict format, need to add back later

        # Save to Json
        new_car = Car(content=content)
        db_err = foo.db_add_one(new_car, db)

        if db_err is not None:
            return db_err

        flag = 1
        return redirect('/')

    else:
        # don't forget return
        return render_template('typein.html') # hold Ctrl and click You can go that website page


@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        df = pd.read_csv(f)
        for index, row in df.iterrows():

            form = {k: row[k] for k in ["Name", "Mileage", "Condition", "Price", "Dealer", "Count of ratings", "Reviews"]}
            # form = {k: row[k] for k in ["Name", "Mileage", "Condition", "Year", "Price", "Dealer","Count of ratings", "Reviews"]}

            
            item_json = json.dumps(form)

            # Save to Json 
            new_car = Car(content=item_json)
            
            db_err = foo.db_add_one(new_car, db)

            if db_err is not None:
                return db_err
        flag = 1
        return redirect('/')
    else:
        return render_template('upload.html')

@app.route('/delete/<int:id>')
def delete(id):
    car_to_delete = Car.query.get_or_404(id)

    try:
        db.session.delete(car_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that car'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    car = Car.query.get_or_404(id)

    if request.method == 'POST':
        car.content = request.form['content']

        try:
            db.session.commit()
            flag = 1
            return redirect('/')
        except:
            return 'There was an issue updating your car'

    else:
        return render_template('update.html', car=car)

@app.route('/table')
def table():
    cars = Car.query.order_by(Car.date_created).all()
    for car in cars:
        # Download Image
        car.content = json.loads(car.content)

        if car.content.get('ImageURL') is not None:
            try:
                df = Dv4ddcPreproc.apply_all(df)
                ImageURL = car.content['ImageURL']
                response = requests.get(ImageURL)
                base64img = "data:image/png;base64," \
                    + b64encode(response.content).decode('ascii')
                car.content['Image'] = base64img
            except:
                pass

        car.content = ImmutableMultiDict(car.content)

    return render_template('table.html', cars=cars)

@app.route('/graph')
def graph():
    if 'car' not in locals():
        cars = Car.query.order_by(Car.date_created).all()
    
    cars_content = []
    for car in cars:
        # Download Image
        cars_content += [json.loads(car.content)]

    df = pd.DataFrame(cars_content)

    df.sort_values("Mileage", inplace=True)
    df = Dv4ddcPreproc.apply_all(df)
    fig = px.scatter(df, x='Mileage', y='Price', color='Name')# color='Condition'
    # fig.update_xaxes(range=[1990, 2024])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graph.html', graphJSON=graphJSON)

##############  Bar Chart #############
@app.route('/bar')
def bar():
    if 'car' not in locals():
        cars = Car.query.order_by(Car.date_created).all()
    
    cars_content = []
    for car in cars:
        # Download Image
        cars_content += [json.loads(car.content)]

    df = pd.DataFrame(cars_content)

    # df.sort_values("Mileage", inplace=True)
    # df = Dv4ddcPreproc.apply_all(df)
    fig = px.bar(df, x='Name', y='Reviews')# color='Condition'

    # fig = px.bar(df, x='Mileage', y='Price', color='Name', barmode='group')# color='Condition'
    
    # fig.update_xaxes(range=[1990, 2024])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('bar.html', graphJSON=graphJSON)


##############  PIE Chart #############
# @app.route('/pie')
# def pie():
#     if 'car' not in locals():
#         cars = Car.query.order_by(Car.date_created).all()
    
#     cars_content = []
#     for car in cars:
#         # Download Image
#         cars_content += [json.loads(car.content)]

#     df = pd.DataFrame(cars_content)

#     # df.sort_values("Mileage", inplace=True)
#     # df = Dv4ddcPreproc.apply_all(df)
#     fig = px.pie(df, x='Name', y='Reviews')# color='Condition'

#     # fig = px.bar(df, x='Mileage', y='Price', color='Name', barmode='group')# color='Condition'
    
#     # fig.update_xaxes(range=[1990, 2024])
#     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#     return render_template('pie.html', graphJSON=graphJSON)

if __name__ == "__main__": # entry point of entering flask application
    app.run(debug=True)
