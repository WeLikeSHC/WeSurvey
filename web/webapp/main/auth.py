# coding=utf-8

from flask import Blueprint, render_template, session, redirect, url_for
import xmlrpclib
from flask import current_app

auth = Blueprint("auth", __name__)


@auth.route("/show/<key>", methods=['GET', 'POST'])
def show_info(key):
    session['key'] = key
    return redirect(url_for('auth.index'))


@auth.route("/", methods=['GET', 'POST'])
def index():
    rpc_server = xmlrpclib.Server("http://{}".format(current_app.config['RPC_ADDRESS']))
    rpc_info = rpc_server.get_online_protocol()
    return render_template('index.html', backend=current_app.config['UI_ADDRESS'], info_list=rpc_info)
