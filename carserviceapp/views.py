import io
import json
from os.path import exists
from datetime import datetime
from unicodedata import category
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from flask import Blueprint, redirect, render_template, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, true
from carserviceapp.models import Client, Service, Part, Master, Repair, repair_parts
from carserviceapp import PLATOFRM, db


views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    if current_user.usertype == 'manager':
        return redirect(url_for('views.clients'))
    elif current_user.usertype == 'logistics':
        return redirect(url_for('views.storage'))
    elif current_user.usertype == 'financier':
        return redirect(url_for('views.repair_report'))
    return '<p>Fuck</p>'


# MANAGER
@views.route('/clients', methods=['GET','POST'])
@login_required
def clients():
    if current_user.usertype != 'manager':
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        client_name = request.form.get('name')
        client_phone = request.form.get('phone')
        client_car = request.form.get('car')
        
        if len(client_name) < 1:
            flash('Имя клиента слишком короткое', category='wawrning')
        else:
            new_client = Client(name=client_name, phone=client_phone, car=client_car)
            db.session.add(new_client)
            db.session.commit()
            flash('Клиент добавлен!', category='success')
            return redirect(url_for('views.clients'))
    clients = Client.query.all()
    return render_template('manager/clients.html', user=current_user, clients=clients)

@views.route('/repair', methods=['GET','POST'])
@login_required
def repair():
    if current_user.usertype != 'manager':
        return redirect(url_for('views.home'))
    services = Service.query.all()
    masters = Master.query.all()
    clients = Client.query.all()
    repairs = Repair.query.all()
    parts = Part.query.all()
    if request.method == 'POST':
        if 'date_search' in request.form:
            x = datetime.strptime(request.form.get('from'), f'%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            y = datetime.strptime(request.form.get('to'), f'%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            if x == y:
                repairs = Repair.query.filter_by(date=x)
            elif not x > y :
                
                # print(repairs[0].date.replace(hour=0, minute=0, second=0, microsecond=0), x == repairs[0].date.replace(hour=0, minute=0, second=0, microsecond=0))
                repairs = Repair.query.filter(and_(Repair.date >= x, Repair.date <= y))

            return render_template('manager/repair.html', user=current_user, services=services, masters=masters, clients=clients, repairs=repairs, parts=parts)
        elif 'show_all' in request.form:
            pass
        else:
            repair_client = request.form.get('client')
            repair_service = request.form.get('service')
            repair_master = request.form.get('master')
            repair_part = request.form.getlist('part')
            repair_price = Service.query.filter_by(id=repair_service).first().price
            new_repair = Repair(price=repair_price, client_id=repair_client, master_id=repair_master,service_id=repair_service, date=datetime.strptime('2022-05-01', f'%Y-%m-%d'))
            for rep_par in repair_part:
                # if rep_par.amount > 0:
                part = Part.query.get(rep_par)
                new_repair.parts.append(part)
                new_repair.price += Part.query.filter_by(id=rep_par).first().price
                # else:
                #     flash('Не хватает деталей!', category='danger')
                #     return redirect(url_for('views.repair'))
            # new_repair.price = Part.query.filter_by(id=repair_part).first().price
            db.session.add(new_repair)
            db.session.commit()
            flash('Ремонт добавлен!', category='success')
            return redirect(url_for('views.repair'))
        
    return render_template('manager/repair.html', user=current_user, services=services, masters=masters, clients=clients, repairs=repairs, parts=parts)


@views.route('/parts', methods=['GET', 'POST'])
@login_required
def parts():
    if current_user.usertype != 'manager':
        return redirect(url_for('views.home'))
    repairs = Repair.query.all()
    parts = Part.query.all()
    if request.method == 'POST':
        repair = Repair.query.get(request.form.get('repair'))        
        if repair:
            return render_template('manager/parts.html', user=current_user, selected_repair=repair, parts=parts, repairs=repairs)
    return render_template('manager/parts.html', user=current_user, parts=parts, repairs=repairs)


@views.route('/services', methods=['GET', 'POST'])
@login_required
def services():
    if current_user.usertype != 'manager':
        return redirect(url_for('views.home'))
    services = Service.query.all()
    if request.method == 'POST':  
        if 'price_search' in request.form:
            x = int(request.form.get('from'))
            y = int(request.form.get('to'))
            if not x > y:
                services = Service.query.filter(and_(Service.price >= x, Service.price <= y))
        elif 'name_search' in request.form:
            to_find = request.form.get('to_find')
            services = Service.query.filter_by(name=to_find).all()
    return render_template('manager/services.html', user=current_user, services=services)


@views.route('/repair_done', methods=['POST'])
@login_required
def repair_done():
    repair = json.loads(request.data)
    repairId = repair['repairId']
    repair = Repair.query.get(repairId)
    if repair:
        parts = [id for id in repair.parts]
        for part in parts:
            if part.amount == 0:
                flash('Не хватает деталей!', category='warning')
                return redirect(url_for('views.repair'))
            part.amount -= 1
            part.discontinued += 1
            repair.status = 'Готово'
            db.session.commit()
    return redirect(url_for('views.repair'))


# LOGISTICS
@views.route('/storage', methods=['GET', 'POST'])
@login_required
def storage():
    if current_user.usertype != 'logistics':
        return redirect(url_for('views.home'))
    parts = Part.query.all()
    countries = {x.country for x in parts}
    if request.method == 'POST':
        part = request.form.get('part_id')
        if request.form.get('amount') != None:
            amount = int(request.form.get('amount'))
        if 'price_search' in request.form:
            x = int(request.form.get('from'))
            y = int(request.form.get('to'))
            country = request.form.get('country_search')
            if x == 0 and y == 0:
                print(country)
                if country != None:
                    parts = Part.query.filter_by(country=country)
                else:
                    parts = Part.query.all()
            elif not x > y:
                if country == None:
                    parts = Part.query.filter(and_(Part.price >= x, Part.price <= y))
                else:
                    parts = Part.query.filter(and_(Part.price >= x, Part.price <= y, Part.country == country))
        elif 'name_search' in request.form:
            to_find = request.form.get('to_find')
            parts = Part.query.filter_by(name=to_find).all()
        elif 'add' in request.form:
            Part.query.filter_by(id=part).first().amount += amount
            db.session.commit()
            flash(f'Добавлено {amount} деталей!', category='success')
            return redirect(url_for('views.storage'))
        elif 'subtract' in request.form:
            if Part.query.filter_by(id=part).first().amount - amount > 0:
                Part.query.filter_by(id=part).first().amount -= amount
                Part.query.filter_by(id=part).first().discontinued += 1
                db.session.commit()
                flash(f'Списано {amount} деталей!', category='warning')
                return redirect(url_for('views.storage'))
            else:
                flash('Больше деталей списать нельзя!', category='danger')
                return redirect(url_for('views.storage'))
        elif 'discontinue' in request.form:
            name = Part.query.filter_by(id=part).first().name
            db.session.delete(Part.query.filter_by(id=part).first())
            db.session.commit()
            flash(f'Деталь {name} удалдена!', category='warning')
            return redirect(url_for('views.storage'))
        elif 'new_part' in request.form:
            part_vendor_code = request.form.get('vendor_code')
            part_name = request.form.get('name')
            part_price = request.form.get('price')
            part_country = request.form.get('country')
            new_part = Part(vendor_code=part_vendor_code, name=part_name, price=part_price, country=part_country, amount=1)
            db.session.add(new_part)
            db.session.commit()
            flash(f'Деталь "{part_name}" добавлена на склад', category='success')
            return redirect(url_for('views.storage'))
        elif 'show_all' in request.form:
            pass
    return render_template('logistics/storage.html', user=current_user, parts=parts, countries=countries)



# FINANCIER
@views.route('/parts_report', methods=['GET', 'POST'])
@login_required
def parts_report():
    if current_user.usertype != 'financier':
        return redirect(url_for('views.home'))
    parts = Part.query.all()
    used_parts = sum([x.discontinued for x in parts])
    wasted_on_parts = sum([x.price*x.discontinued for x in parts if x.discontinued > 0])
    if request.method == 'POST':
         if 'price_search' in request.form:
            x = int(request.form.get('from'))
            y = int(request.form.get('to'))
            if not x > y:
                parts = Part.query.filter(and_(Part.price >= x, Part.price <= y))
                used_parts = sum([x.discontinued for x in parts])
                wasted_on_parts = sum([x.price*x.discontinued for x in parts if x.discontinued > 0])
            elif 'show_all' in request.form:
                pass
    return render_template('financier/parts_report.html', user=current_user, parts=parts, used_parts=used_parts, wasted_on_parts=wasted_on_parts)


@views.route('/repair_report', methods=['GET', 'POST'])
@login_required
def repair_report():
    if current_user.usertype != 'financier':
        return redirect(url_for('views.home'))
    clients = Client.query.all()
    repairs = Repair.query.all()
    masters = Master.query.all()
    earnings = sum([x.price for x in repairs if x.status == 'Готово'])
    if request.method == 'POST':
        if 'date_search' in request.form:
            x = datetime.strptime(request.form.get('from'), f'%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            y = datetime.strptime(request.form.get('to'), f'%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            if x == y:
                repairs = Repair.query.filter_by(date=x)
                earnings = sum([x.price for x in repairs if x.status == 'Готово'])
            elif not x > y :
                repairs = Repair.query.filter(and_(Repair.date >= x, Repair.date <= y))
                earnings = sum([x.price for x in repairs if x.status == 'Готово'])
        elif 'show_all' in request.form:
            pass
        elif 'master_search' in request.form:
            master = request.form.get('master')
            repairs = Repair.query.filter_by(master_id=master).all()
    return render_template('financier/repair_report.html', user=current_user, clients=clients, repairs=repairs, masters=masters, earnings=earnings)


@views.route('/statistics', methods=['GET', 'POST'])
@login_required
def statistics():
    if current_user.usertype != 'financier':
        return redirect(url_for('views.home'))
    repairs = Repair.query.all()
    clients = Client.query.all()
    parts = Part.query.all()
    car_repair = {}
    used_parts = {}

    for x in clients:
        car_repair[x.car] = 0
        for y in repairs: 
            if x.id == y.client_id:
                car_repair[x.car] += 1
                
    for x in parts:
        used_parts[x.name] = 0
        if x.discontinued > 0:
            used_parts[x.name] += x.discontinued
            
    earnings = sum([x.price for x in repairs if x.status == 'Готово'])
    parts_price = sum([x.price*x.amount for x in parts])
    assumed_earnings = {'Прибыль': earnings, 'Потрачено на детали': parts_price}
    create_figure(car_repair, 'graph1', 'Выполненные ремонты по маркам автомобилей')
    create_figure(used_parts, 'graph2', 'Использованные запчасти по наименованиям')
    create_figure(assumed_earnings, 'graph3', 'Cредний чек всех работ')
           
    return render_template('financier/statistics.html', user=current_user)


def create_figure(data, name, title):
    plt.style.use('seaborn-pastel')
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title(title)
    slices = data.values()
    labels = data.keys()
    axis.pie(slices, labels=labels, 
            shadow=True,
            autopct='%1.1f%%',
             startangle=90,
            wedgeprops={'edgecolor': '#6f6f6f'})
    axis.legend(labels=slices, loc='upper center', 
           bbox_to_anchor=(0.1, 0.04), ncol=2)
    fig.savefig(f'carserviceapp/static/graphs/{name}.png', dpi=300, transparent=True)
