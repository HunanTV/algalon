#!/usr/bin/env python
# coding=utf-8

from flask import render_template, redirect, url_for, flash, g, current_app, request
from urlparse import urlparse
from . import main
from .forms import EditProfileForm, NewProjectForm, NewToEmailForm
from .. import db
from ..models import User, Project, ToEmail, Alarm
from ..decorators import login_required

import re

@main.route('/')
def index():
    if g.user:
        return redirect(url_for('.user', username=g.user.username))
    return render_template('index.html')


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    url = current_app.config['ALGALON_SERVER_HOST']
    urlparts = urlparse(url)
    port = current_app.config['ALGALON_SERVER_PORT']
    return render_template('user.html', user=user,  host=urlparts.netloc, port=port)


@main.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfileForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        user.name = form.name.data
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.user', username=username))
    return render_template('edit_profile.html', form=form)


@main.route('/user/<username>/project/<project_name>')
@login_required
def user_project(username, project_name):
    user = User.query.filter_by(username=username).first_or_404()
    project = user.projects.filter_by(name=project_name).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = project.alarms.order_by(Alarm.date_added.desc()).paginate(
        page,5,
        error_out=False)
    alarms = pagination.items
    return render_template('project.html', username=user.username,
                           alarms=alarms, project=project,
                           pagination=pagination)


@main.route('/user/<username>/project/<project_name>/reset_token')
@login_required
def reset_token(username, project_name):
    user = User.query.filter_by(username=username).first_or_404()
    project = user.projects.filter_by(name=project_name).first_or_404()
    project.reset_token()
    db.session.add(project)
    db.session.commit()
    return redirect(url_for('.user', username=username))


@main.route('/user/<username>/project/new', methods=['GET', 'POST'])
@login_required
def create_user_project(username):
    form = NewProjectForm()
    if form.validate_on_submit():
        project_name = form.name.data
        if g.user.projects.filter_by(name=project_name).first():
            flash('failure, project name already exist')
            return redirect(url_for('.user', username=username))
        project = Project(name=project_name)
        g.user.projects.append(project)
        db.session.add(g.user)
        db.session.commit()
        flash('new project created')
        return redirect(url_for('.user', username=username))
    return render_template('new_project.html', form=form)


@main.route('/user/<username>/project/<project_name>/delete')
@login_required
def delete_project(username, project_name):
    user = User.query.filter_by(username=username).first_or_404()
    project = user.projects.filter_by(name=project_name).first_or_404()
    user.projects.remove(project)
    db.session.add(user)
    db.session.commit()
    flash('project deleted')
    return redirect(url_for('.user', username=username))


@main.route('/<username>/<project_name>/to_email/new', methods=['GET', 'POST'])
@login_required
def create_to_email(username, project_name):
    p = g.user.projects.filter_by(name=project_name).first_or_404()
    form = NewToEmailForm()
    if form.validate_on_submit():
        pt = re.compile('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$')
        addresses = form.addresses.data

        for address in set([x.strip() for x in addresses.split(',')]):
            m = pt.match(address)
            if m:
                te = ToEmail(address=m.group())
                p.to_emails.append(te)

        db.session.add(p)
        db.session.commit()
        flash('emails added')
        return redirect(url_for('.user_project', username=username, project_name=project_name))
    return render_template('new_to_email.html', form=form)


@main.route('/<username>/<project_name>/<to_email_id>/delete', methods=['GET'])
@login_required
def delete_to_email(username, project_name, to_email_id):
    p = g.user.projects.filter_by(name=project_name).first_or_404()
    te = p.to_emails.filter_by(id=to_email_id).first_or_404()
    p.to_emails.remove(te)
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('.show_to_emails', username=username, project_name=project_name))


@main.route('/<username>/<project_name>/to_emails', methods=['GET'])
@login_required
def show_to_emails(username, project_name):
    user = User.query.filter_by(username=username).first_or_404()
    project = user.projects.filter_by(name=project_name).first_or_404()
    return render_template('to_emails.html', username=username, project=project)
