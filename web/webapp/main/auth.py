# coding=utf-8

from flask import Blueprint, render_template, redirect, url_for, session, flash
import xmlrpclib
import requests
from models import User
from .. import online
from form import InputForm
from flask import current_app, request
from flask_login import login_required, current_user, login_user
import json

auth = Blueprint("auth", __name__)


@auth.route("/show/<key>", methods=['GET', 'POST'])
@login_required
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
    url = "https://cherrymonth.top/get_user_info/?email={}&password={}".format(email, password)
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
        if session.get('key'):
            del session['key']
        flash(u"登出成功!", "success")
    else:
        flash(u"您尚未登录,无法注销!", "warning")
    return redirect(url_for("auth.index"))


@auth.route("/node_info/<_node>", methods=['GET', 'POST'])
@login_required
def node_info(_node):
    if request.method == "GET":
        return render_template("node_info.html", node=_node, backend=current_app.config['UI_ADDRESS'])
    return redirect(url_for("auth.node_info", node=_node))


@auth.route("/node", methods=['GET', 'POST'])
@login_required
def node():
    rpc_server = xmlrpclib.Server("http://{}".format(current_app.config['RPC_ADDRESS']))
    node_list = map(lambda x: json.loads(x), rpc_server.get_online_node())
    print(node_list)
    return render_template("node.html", node_list=node_list)


@auth.route("/word_cloud", methods=['GET', 'POST'])
def word_cloud():
    form = InputForm()
    if request.method == "POST":
        try:
            if form.algorithm.data == "dfs":
                form.algorithm.data = "深度优先搜索"
            else:
                form.algorithm.data = "广度优先搜索"
            rpc_server = xmlrpclib.Server("http://{}".format(current_app.config['RPC_ADDRESS']))
            status = rpc_server.add_job(str(form), current_user.id)
            if(status['status']) != 200:
                flash(status['info'], "warning")
        except Exception as e:
            flash(str(e), "warning")
        return redirect(url_for("auth.word_cloud"))
    work_list = list()
    try:
        rpc_server = xmlrpclib.Server("http://{}".format(current_app.config['RPC_ADDRESS']))
        work_list = rpc_server.get_work_info(current_user.id)
    except Exception as e:
        flash(str(e), "warning")
    return render_template("word_cloud.html", form=form, work_list=work_list, backend=current_app.config['UI_ADDRESS'])
