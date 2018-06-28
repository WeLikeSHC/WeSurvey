# coding=utf-8

from flask_wtf import FlaskForm
import json
from wtforms import StringField, SelectField, TextAreaField, SubmitField


class InputForm(FlaskForm):
    url = StringField(u"网站地址")
    number = StringField(u'数量')
    dispersion = StringField(u'离散度')
    algorithm = SelectField(u"网页遍历算法选择")
    submit = SubmitField(u"提交")

    def __str__(self):
        return json.dumps({'url': "<a href='{}' target='_blank'>".format(self.url.data) + self.url.data + "</a>",
                           'number': self.number.data, "dispersion": self.dispersion.data,
                           "algorithm": "<a>" + self.algorithm.data + "</a>",
                           "result": "<a href='#'>暂无</a>"})
