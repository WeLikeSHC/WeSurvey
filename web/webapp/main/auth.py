# coding=utf-8

from flask import Blueprint, render_template, redirect, url_for, session, flash
import xmlrpclib
import requests
from models import User
from .. import online
from flask import current_app, request
from flask_login import login_required, current_user, login_user
import json

auth = Blueprint("auth", __name__)


@login_required
@auth.route("/show/<key>", methods=['GET', 'POST'])
def show_info(key):
    session['key'] = key
    return redirect(url_for('auth.index'))


@auth.route("/", methods=['GET', 'POST'])
def index():
    rpc_info = list()
    if current_user.is_authenticated:
        try:
            rpc_server = xmlrpclib.Server("http://{}".format(current_app.config['RPC_ADDRESS']))
            rpc_info = rpc_server.get_online_protocol()
            print rpc_info
            for rpc in rpc_info:
                if rpc and rpc[1]['user_id'] != str(current_user.id):
                    rpc_info.remove(rpc)
        except Exception as e:
            flash(u"后端服务异常,请联系管理员!", "warning")
            print e

    return render_template('index.html', backend=current_app.config['UI_ADDRESS'], info_list=rpc_info)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    email = request.args.get('email')
    password = request.args.get('password')
    url = "http://cherrymonth.top:5000/get_user_info/?email={}&password={}".format(email, password)
    ret = requests.post(url)
    info = json.loads(ret.text)
    if info != '{}' and info:
        user = User()
        user.email = info.get('email')
        user.image_name = info.get('image_name')
        user.username = info.get('username')
        user.about_me = info.get('about_me')
        user.id = info.get('id')
        online[int(user.id)] = user
        '''
        flask_login 只能登录在数据库中存在的用户 因为load_user 会查询当前用户的id与数据库的进行比对
        我数据库没有数据只是凭借创建的对象进行登录无法进行验证。
        而现在我采用了一个在线用户的列表 存储用户的id与实例 验证用户是否登录时首先把当前用户的id与在线列表中的id进行比对 若存在则登录成功
        '''

        login_user(user)
        flash(u'登录成功!', "success")
    else:
        flash(u'密码错误或者用户不存在!', "warning")
    return redirect(url_for("auth.index"))


@auth.route("/logout", methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        del online[current_user.id]
        del session['key']
        flash(u"登出成功!", "success")
    else:
        flash(u"您尚未登录,无法注销!", "warning")
    return redirect(url_for("auth.index"))
