# -*- coding=utf-8 -*-
import re
from django import forms
from django.forms import fields
from movie import models
from django.core.validators import RegexValidator

class RegisterForms(forms.Form):
    username = fields.CharField(
        error_messages={'required':'用户名不能为空'}
    )
    email = fields.EmailField(
        error_messages={'required': '邮箱不能为空',
                        'invalid': '邮箱格式错误'}
    )
    password = fields.CharField(
        error_messages={'required':'密码不能为空',
                        },
    )
    code = fields.CharField(
        error_messages={'required': '验证码不能为空'}
    )

    def clean_password(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data['password'].replace(' ','')
        if len(password) < 6:
            raise forms.ValidationError("密码长度不能小于6个字符")
        return password


    # python匹配中文需要转换成unicode字符串
    def clean_username(self):
        cleaned_data = self.cleaned_data
        reg_username = cleaned_data['username']
        pattern = re.compile(u'^[\u4e00-\u9fa5_a-zA-Z0-9-]{3,16}$')
        match = pattern.match(unicode(reg_username))
        if match:
            return reg_username
        else:
            raise forms.ValidationError("用户名长度为3~16个字符，支持中文，数字，字母，下划线，横杠")

class EmailForms(forms.Form):
    email = fields.EmailField(
        error_messages={'required': '邮箱不能为空',
                        'invalid': '邮箱格式错误'}
    )

class UserForms(forms.Form):
    username = fields.CharField(
        error_messages={'required':'用户名不能为空'},
        validators=[RegexValidator('^[\u4e00-\u9fa5_a-zA-Z0-9-]+$', '用户名只能包含中文，数字，字母，下划线，横杠')],
    )

class LoginForms(forms.Form):
    username = fields.CharField(
        error_messages={'required':'用户名不能为空'}
    )
    password = fields.CharField(
        error_messages={'required':'密码不能为空'}
    )
    code = fields.CharField(
        error_messages={'required': '验证码不能为空'}
    )
    #
    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     try:
    #         u = cleaned_data['username']
    #         e = cleaned_data['email']
    #         p = cleaned_data['password']
    #         exists = models.UserInfo.objects.filter((Q(username=u) & Q(password=p)) | Q(Q(email=e) & Q(password=p)))
    #         if exists:
    #             pass
    #         else:
    #             raise forms.ValidationError('账号或密码错误')
    #     except Exception as e:
    #         print 'has a error--->',e
    #     return self.cleaned_data

class EditorForms(forms.Form):
    '''
    编辑框form验证留作备用
    '''
    revi_title = fields.CharField(
        error_messages={'required':'标题不能为空'}
    )
    revi_content = fields.CharField()


    def clean_revi_content(self):
        cleaned_data = self.cleaned_data
        revi_content = cleaned_data['revi_content']
        pattern = re.compile(r'<[^>]+>', re.S)
        ret = pattern.sub('', revi_content)
        if not ret:
            raise forms.ValidationError('你咋还没写正文呢')
        else:
            return ret

class CommentForms(forms.Form):
    comment_content = fields.CharField()
class ReplyForms(forms.Form):
    reply_content = fields.CharField()


