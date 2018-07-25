# -*- coding=utf-8 -*-
import json
import io
import re
import datetime
import time
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from movie import models
from movie.models import Review
from django.db.models import Q
from movie.utils.pagin import PaginationCustom
from movie.utils.random_code import random_code
from movie.utils.send_msg import send_email
from movie.utils.check_code import create_validate_code
from movie.utils.random_num import randomNum
from movie.utils.datetime_serialize import datetime_handle
from .customforms import LoginForms, EmailForms, UserForms, RegisterForms, EditorForms, CommentForms, ReplyForms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from itertools import chain
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView


class IndexView(ListView):
    models = models.MovieAndTv
    template_name = 'index.html'
    context_object_name = 'movietv_list'

    def get_queryset(self):
        movietv_list = models.MovieAndTv.objects.all().order_by('-ctime')[:10]
        return movietv_list


def movie_list(request, **kwargs):
    '''
    多条件搜索+排序+分页 
    '''
    pid = kwargs['pid']
    ty = int(kwargs['m_to_type'])
    ar = int(kwargs['m_to_area'])
    ti = int(kwargs['f_to_time_id'])
    sort_type = kwargs['sort']

    # 排序
    st = None
    if sort_type == 'time':
        st = '-ctime'
    elif sort_type == 'grade':
        st = '-grade'
    # 热度排序未定义（考虑点击量，下载量）  默认default
    else:
        st = '-ctime'

    # 多条件搜索(组合搜索)
    kwargs['m_to_type'] = ty
    kwargs['m_to_area'] = ar
    kwargs['f_to_time_id'] = ti

    ty_q = Q(m_to_type__id=ty)
    ar_q = Q(m_to_area__id=ar)
    ti_q = Q(f_to_time_id=ti)
    ca_q = Q(f_to_category_id=1)

    conditions = None
    # 三项id都为0的情况
    if ty == 0 and ar == 0 and ti == 0:
        conditions = ca_q
    # 三项id都不为0的情况
    elif ty != 0 and ar != 0 and ti != 0:
        conditions = ar_q & ty_q & ti_q & ca_q
    else:
        # 其中一项id为0的情况
        if ty == 0:
            conditions = ar_q & ti_q & ca_q
        elif ar == 0:
            conditions = ty_q & ti_q & ca_q
        elif ti == 0:
            conditions = ar_q & ty_q & ca_q
        # 其中两项id为0的情况
        if ty == 0 and ar == 0:
            conditions = ti_q & ca_q
        elif ty == 0 and ti == 0:
            conditions = ar_q & ca_q
        elif ar == 0 and ti == 0:
            conditions = ty_q & ca_q
    # 根据组合条件匹配到的结果的条目数，用于计算分页的页数
    items_count = models.MovieAndTv.objects.all().filter(conditions).count()

    # 分页，调用自定义分页模块
    path_info = request.path_info
    base_url = '/'.join(path_info.split('/')[1:-1])
    pagin = PaginationCustom(pid, items_count, base_url, start=None, end=None)
    pagin.get_total_page()

    # 根据组合条件,排序字段，数据库切片操作，获取结果集
    if st is None:
        items = models.MovieAndTv.objects.all().filter(conditions)[pagin.start:pagin.end]
    else:
        items = models.MovieAndTv.objects.all().filter(conditions).order_by(st)[pagin.start:pagin.end]

    # 生成分页html
    page_list = pagin.get_page_list()
    # 没有数据时，什么都不显示
    if not page_list:
        page_list = ''

    type_list = models.MovieAndTvType.objects.all()
    area_list = models.MovieAndTvArea.objects.all()
    time_list = models.MovieAndTvTime.objects.all()

    # 用于sort.html中的拼接url
    path_info = request.path_info
    current_url = '/'.join(path_info.split('/')[:3])

    return render(request, 'mov-list.html', {'type_list': type_list,
                                             'area_list': area_list,
                                             'time_list': time_list,
                                             'kwargs': kwargs,
                                             'items': items,
                                             'page_list': page_list,
                                             'current_url': current_url})


def tv_list(request, **kwargs):
    '''
    逻辑与movie_list相同
    '''
    pid = kwargs['pid']
    area = int(kwargs['m_to_area'])
    sort_type = kwargs['sort']

    st = None
    if sort_type == 'time':
        st = '-ctime'
    elif sort_type == 'grade':
        st = '-grade'
    else:
        st = '-ctime'

    # conditions = ()
    ar_q = Q()
    ca_q = Q(f_to_category_id=2)
    if area == 0:
        ar_q = Q()
    elif area == 1:
        ar_q = Q(m_to_area__id=2)
    elif area == 2:
        ar_q = Q(m_to_area__id=7)
    elif area == 3:
        ar_q = Q(m_to_area__id=1)
    elif area == 5:
        ar_q = Q(m_to_area__id=5)
    elif area == 6:
        ar_q = Q(m_to_area__id=6)
    # 其他,需要去重 distinct()
    elif area == 7:
        ar_q = Q(m_to_area__id__gt=7)
    conditions = ar_q & ca_q

    # 港台剧单独设计过滤条件
    if area == 4:
        ar_q_1 = Q(m_to_area__id=3)
        ar_q_2 = Q(m_to_area__id=4)
        conditions = ca_q & (ar_q_1 | ar_q_2)

    # 根据过滤条件获得条目总数  去重
    items_count = models.MovieAndTv.objects.all().filter(conditions).distinct().count()

    # 分页
    path_info = request.path_info
    # base_url -->tv/7/default
    base_url = '/'.join(path_info.split('/')[1:-1])
    pagin = PaginationCustom(pid, items_count, base_url, start=None, end=None)
    pagin.get_total_page()

    # 排序规则  去重
    if st is None:
        items = models.MovieAndTv.objects.all().filter(conditions).distinct()[pagin.start:pagin.end]
    else:
        items = models.MovieAndTv.objects.all().filter(conditions).distinct().order_by(st)[pagin.start:pagin.end]

    # 当数据条目小于等于40  则不生成分页 将空[] 转换为 ''
    page_list = pagin.get_page_list()
    if not page_list:
        page_list = ''

    path_info = request.path_info
    current_url = '/'.join(path_info.split('/')[:3])

    return render(request, 'tv-list.html', {'items': items,
                                            'page_list': page_list,
                                            'current_url': current_url})


@csrf_exempt
def movietv_detail(request, nid):
    '''
    详情页，mov 和 tv 指向同一个视图
    '''
    query = False
    items = get_object_or_404(models.MovieAndTv, num=nid)
    user_obj = get_object_or_404(models.UserInfo, username=request.user)

    # user_obj = models.UserInfo.objects.filter(username=request.user).first()
    if request.method == 'GET':
        # 根据用户id获取第三张表中对应的所有movietv_id，如果判断当前页面movietv_id在其中，则显示‘已收藏’
        # 用户未登录时 user_obj显示为None
        if user_obj:
            movietv_obj_list = models.Collect.objects.filter(coll_user_id=user_obj.id)
            movietv_list = []
            for row in movietv_obj_list:
                movietv_list.append(row.coll_movietv_id)
            if items.id in movietv_list:
                query = True


        request.session['login_from'] = request.path_info

        # torrent_title，torrent这两个字段保存了一条或多条数据，将其就由字符串转换为列表再合并为字典，方便前端展示
        def str_to_list(before_data):
            after_data = before_data.split(',')
            return after_data
        tt_list = str_to_list(items.torrent_title)
        t_list = str_to_list(items.torrent)
        torrent_items = dict(zip(tt_list, t_list))


        # 该影视下的所有评论
        comm_items = models.MovieTvComment.objects.filter(comm_movietv_num=int(nid)).order_by('-ctime')
        # 通过released_name查找所有评论下所有的回复，并合并结果集
        reply_items = models.ReplyMovieTvComment.objects.none()
        for row in comm_items:
            reply_items = reply_items | row.comment_has_reply.all()

        return render(request, 'movietv-detail.html', {'items': items,
                                                       'reply_items': reply_items,
                                                       'torrent_items': torrent_items,
                                                       'query': query,
                                                       'comm_items': comm_items})

    elif request.method == 'POST':
        ret = {'status': True}
        obj = CommentForms(request.POST)
        if obj.is_valid():
            content = obj.cleaned_data['comment_content']

            # 毫秒时间戳
            current_milli_time = lambda: int(round(time.time() * 1000))
            comm_num =  str(current_milli_time())[4:-1]

            # 添加评论
            comment_obj = models.MovieTvComment.objects.create(comm_movietv_num_id=int(nid),
                                                               comm_user_num_id=user_obj.user_num,
                                                               comm_num =comm_num,
                                                                m_content=content)

            #　显示留言总数，方便最近添加的留言的楼数----> #xx  因为forloop.count没放在模板for循环中  无法生成最新的楼数
            comment_count = models.MovieTvComment.objects.filter(comm_movietv_num_id=int(nid)).count()

            # 将html转义 防止js注入攻击
            import cgi
            content = cgi.escape(comment_obj.m_content)

            # 数据传到前端，ajax追加HTML，数据渲染
            ret['content'] = content
            ret['user_num'] = user_obj.user_num
            ret['username'] = user_obj.username
            ret['ctime'] = comment_obj.ctime
            ret['comment_count'] = comment_count
            ret['comm_num'] = comm_num

            # datetime类型自定义序列化
            return HttpResponse(json.dumps(ret, default=datetime_handle))
        else:
            ret['status'] = False
            return HttpResponse(json.dumps(ret))


def n_v(request):
    '''
    建设中
    '''
    return render(request, 'come.html')


@csrf_exempt
def register(request):
    ret = {'status': True, 'error': None, 'data': None}
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        obj = RegisterForms(request.POST)
        if obj.is_valid():
            code = obj.cleaned_data['code']
            email = obj.cleaned_data['email']
            password = obj.cleaned_data['password']
            username = obj.cleaned_data['username']

            # 判断验证码是否超时
            session_exist = request.session.get('EmailCode', None)
            if session_exist:
                if (request.session['EmailCode']).lower() == code.lower():

                    num = randomNum()

                    # make_password  可选salt值和哈希算法
                    # set_password  将用户的密码设置为给定的原始字符串
                    password = make_password(password)
                    models.UserInfo.objects.create(username=username,
                                                   password=password,
                                                   email=email,
                                                   user_num=num)
                    return HttpResponse(json.dumps(ret))
                else:
                    # 验证码错误
                    ret['status'] = 2
                    return HttpResponse(json.dumps(ret))
            else:
                # 验证码超时
                ret['status'] = 1
                return HttpResponse(json.dumps(ret))
        else:
            res_str = obj.errors.as_json()
            ret['status'] = False
            ret['error'] = res_str
        return HttpResponse(json.dumps(ret))


@csrf_exempt
def send_msg(request):
    ret = {'status': True, 'error': None, 'data': None}
    obj = EmailForms(request.POST)
    if obj.is_valid():
    # 通过验证，获取输入数据
        email = obj.cleaned_data['email']
        is_email_exists = models.UserInfo.objects.filter(email=email).exists()
        if is_email_exists:
            # 邮箱已被注册
            ret['status'] = 1
            return HttpResponse(json.dumps(ret))
        else:
            code = random_code()
            content = 'lightbox用户注册:尊敬的用户：您好，您的注册验证码是' + code

            print '这是验证码', code
            # 邮件验证码写入session，5分钟过期
            request.session['EmailCode'] = code
            request.session.set_expiry(300)
            try:
                send_email(email, content)
            except Exception as e:
                print 'has an error--->',e

    else:
        res_str = obj.errors.as_json()
        ret['status'] = False
        ret['error'] = res_str
    return HttpResponse(json.dumps(ret))


@csrf_exempt
def user_exists(request):
    ret = {'status': True, 'error': None, 'data': None}
    obj = UserForms(request.POST)
    if obj.is_valid():
        username = obj.clean()['username']
        is_email_exists = models.UserInfo.objects.filter(username=username).exists()
        if is_email_exists:
            ret['status'] = False
            return HttpResponse(json.dumps(ret))
    else:
        pass
    return HttpResponse(json.dumps(ret))


@csrf_exempt
def check_code(request):
    """
    获取验证码
    :param request:
    :return:
    """
    stream = io.BytesIO()
    # 创建随机字符 code
    # 创建一张图片格式的字符串，将随机字符串写到图片上
    img, code = create_validate_code()
    img.save(stream, "PNG")
    # 将字符串形式的验证码放在Session中
    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())


@csrf_exempt
def user_login(request):
    ret = {'status': True, 'error': None, 'redirect_to': None, 'user_num': None}
    # 从首页直接点击登录，登录成功则跳转到member页面
    # 从detail页面点击登录，登录成功则跳转到detail页面
    # 每次进入detail页面时，自动将当前url写入到session中
    befor_url = request.META.get('HTTP_REFERER', '/')
    if befor_url == 'http://127.0.0.1:8000/':
        ret['redirect_to'] = '/member'
    else:
        ret['redirect_to'] = request.session.get('login_from', None)


    if request.method == 'GET':
        # 判断用户是否登录
        if request.user.is_authenticated():
            user_obj = models.UserInfo.objects.filter(username=request.user).first()
            return HttpResponseRedirect('/member/%s' % user_obj.user_num)
        return render(request, 'registration/login.html')

    elif request.method == 'POST':
        obj = LoginForms(request.POST)
        if obj.is_valid():
            code = obj.cleaned_data['code']
            # 验证码
            if code.lower() != request.session["CheckCode"].lower():
                ret['status'] = 1
                return HttpResponse(json.dumps(ret))
            else:
                username = obj.cleaned_data['username']
                password = obj.cleaned_data['password']
                remember = request.POST.getlist('remember')

                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        # 如果勾选'记住我',写入session，保存登录状态
                        if remember:
                            login(request, user)

                        user_obj = models.UserInfo.objects.filter(username=request.user).first()
                        ret['user_num'] = user_obj.user_num

                        return HttpResponse(json.dumps(ret))
                else:
                    ret['status'] = 2
                    return HttpResponse(json.dumps(ret))
        else:
            res_str = obj.errors.as_json()
            ret['status'] = False
            ret['error'] = res_str
        return HttpResponse(json.dumps(ret))


def user_logout(request):
    """
    用户注销
    """
    logout(request)
    return redirect('/')


@login_required()
def member(request, **kwargs):
    '''
    用户个人主页
    '''
    account = kwargs['account']
    items = models.UserInfo.objects.filter(username=request.user).first()

    # 个人收藏
    collect_obj_list = models.Collect.objects.filter(coll_user_id=items.id).order_by('-date_created')
    # 个人影评
    review_obj_list = models.Review.objects.filter(revi_user_id=items.id).order_by('-date_created')

    # 合并QuerySet并以时间排序
    union_obj_list = sorted(chain(collect_obj_list, review_obj_list), key=lambda instance: instance.date_created, reverse=True)


    content = {'collect_obj_list': collect_obj_list,
               'review_obj_list': review_obj_list,
               'union_obj_list': union_obj_list,
               'items': items}


    if account == 'collect':
        return render(request, 'account/collect.html', content)
    elif account == 'review':
        return render(request, 'account/self_review.html', content)
    elif account == 'revi_detail':
        return render(request, 'account/revi_detail.html', {'items': items})
    elif account == 'comment':
        return render(request, 'account/comment.html', {'items': items})
    elif account == 'info':
        return render(request, 'account/info.html', {'items': items})
    elif account == 'ask':
        return render(request, 'account/ask.html', {'items': items})
    else:
        return render(request, 'member.html', content)


@csrf_exempt
def collect(request):
    '''
    收藏
    '''
    ret = {'login_status': 0}
    # 验证用户是否登录，登录则判断收藏状态，决定是否收藏，未登录则返回给前端'未登录状态'，前端控制跳转
    if request.user.is_authenticated:
        user = request.user
        data = request.POST
        num = data['num']
        collect_status = data['collect_status']

        user_obj = models.UserInfo.objects.filter(username=user).first()
        movietv_obj = models.MovieAndTv.objects.filter(num=int(num)).first()

        # 如果页面显示'收藏',点击之后就添加，反之，则取消收藏
        if int(collect_status) == 1:
            models.Collect.objects.create(coll_user_id=user_obj.id, coll_movietv_id=movietv_obj.id)
        else:
            models.Collect.objects.filter(coll_user_id=user_obj.id, coll_movietv_id=movietv_obj.id).delete()

        ret['login_status'] = 1
        return HttpResponse(json.dumps(ret))
    else:
        return HttpResponse(json.dumps(ret))


@login_required()
@csrf_exempt
def new_review(request):
    '''
    登录用户新建影评
    '''
    review_dict = {}
    ret = {'status': True, 'user_num': None}
    if request.method == 'POST':
        # forms表单验证无法做到错误信息细化
        revi_title = request.POST.get('revi_title')
        content = request.POST.get('revi_content')
        # wangEditor编辑框提交空文本时会附带html标签  <p><br></p>
        pattern = re.compile(r'<[^>]+>', re.S)
        revi_content = pattern.sub('', content)
        if not revi_title and revi_content:
            ret['status'] = 1
            return HttpResponse(json.dumps(ret))
        elif revi_title and not revi_content:
            ret['status'] = 2
            return HttpResponse(json.dumps(ret))
        elif not revi_title and not revi_content:
            ret['status'] = 1
            return HttpResponse(json.dumps(ret))
        else:
            url = request.POST.get('url')
            movietv_num = url.split('/')[-1]

            user = models.UserInfo.objects.filter(username=request.user).first()
            movietv = models.MovieAndTv.objects.filter(num=movietv_num).first()

            num = randomNum()
            review_dict['revi_num'] = num
            review_dict['revi_content'] = request.POST.get('revi_content')
            review_dict['revi_title'] = request.POST.get('revi_title')
            review_dict['revi_user_id'] = user.id
            review_dict['revi_movietv_id'] = movietv.id
            models.Review.objects.create(**review_dict)
            ret['user_num'] = user.user_num
            return HttpResponse(json.dumps(ret))

    else:
        befor_url = request.META.get('HTTP_REFERER', '/')
        movietv_num = befor_url.split('/')[-2]
        items = models.MovieAndTv.objects.filter(num=movietv_num)
        return render(request, 'add_review.html', {'items': items})


@csrf_exempt
def revi(request, nid, category):
    '''
    根据传参的不同，路由映射到同一个views，逻辑处理再分配不同的模板，不知道这样是否合理？？？
    '''
    if request.method == 'GET':

        # url传了id ，revi_detail页面
        if nid:
            # 写入session  方便之后通过revi_num 进行编辑/删除
            request.session['ReviNum'] = nid

            revi_obj = get_object_or_404(Review, revi_num=int(nid))

            revi_obj.increate_views()


            user_obj = models.UserInfo.objects.filter(username=request.user).first()

            query = False
            if user_obj:
                # 当前用户在当前影评上是否有点赞
                vote_exists = models.Vote.objects.filter(vote_user_id=user_obj.id).filter(vote_revi_id=revi_obj.id).exists()
                if vote_exists:
                    query = True

            return render(request, 'account/revi_detail.html', {'revi_obj': revi_obj,
                                                                'query': query})

        # url未传id，revi_list 页面
        if category == 'hot':
            # 聚合review表下的点赞总数，并排序
            revi_list = models.Review.objects.annotate(vote_count=Count('revi_has_vote')).order_by('-vote_count')
            return render(request, 'revi-list.html', {'revi_list': revi_list})

        elif category == 'friend':
            pass
        else:
            pass
        # 默认以更新时间排序
        revi_list = models.Review.objects.all().order_by('-revi_utime')


        return render(request, 'revi-list.html', {'revi_list': revi_list})

    # POST方式访问，该页面必然是revi_detail页面
    # 点赞
    elif request.method == 'POST':
        ret = {'status': True}
        user = request.user
        color_status = request.POST['color_status']
        revi_num = request.POST['revi_num']

        user_obj = models.UserInfo.objects.filter(username=user).first()
        revi_obj = models.Review.objects.filter(revi_num=revi_num).first()

        if int(color_status) == 1:
            models.Vote.objects.create(vote_user_id=user_obj.id,
                                       vote_revi_id=revi_obj.id)
        else:
            models.Vote.objects.filter(vote_user_id=user_obj.id,
                                       vote_revi_id=revi_obj.id).delete()


        return HttpResponse(json.dumps(ret))


@csrf_exempt
def edit_revi(request):
    # 从revi_detail页面跳过来

    if request.method == 'GET':

        revi_num = request.session['ReviNum']
        revi_obj = models.Review.objects.filter(revi_num=int(revi_num)).first()

        items = models.MovieAndTv.objects.filter(id=revi_obj.revi_movietv_id)
        # 将已有的文章标题和内容  渲染到编辑框中  作为初始值
        return render(request, 'account/revi_edit.html', {'revi_obj': revi_obj,
                                                          'items': items})
    elif request.method == 'POST':
        #　文章编辑完了 验证 更新
        ret = {'status': True}
        # forms表单验证无法做到错误信息细化，自行验证
        revi_title = request.POST.get('revi_title')
        content = request.POST.get('revi_content')
        # wangEditor编辑框提交空文本时会附带html标签  <p><br></p>
        pattern = re.compile(r'<[^>]+>', re.S)
        revi_content = pattern.sub('', content)
        if not revi_title and revi_content:
            ret['status'] = 1
            return HttpResponse(json.dumps(ret))
        elif revi_title and not revi_content:
            ret['status'] = 2
            return HttpResponse(json.dumps(ret))
        elif not revi_title and not revi_content:
            ret['status'] = 1
            return HttpResponse(json.dumps(ret))

        else:
            # 更新
            revi_num = request.session['ReviNum']
            revi_content = request.POST.get('revi_content')
            revi_title = request.POST.get('revi_title')

            # auto_now 只支持 save()
            obj = Review.objects.filter(revi_num=revi_num).first()
            obj.revi_content = revi_content
            obj.revi_title = revi_title
            obj.save()
            return HttpResponse(json.dumps(ret))


@csrf_exempt
def del_revi(request):
    '''
    删除影评
    :param request: 
    :return: 
    '''
    ret = {'user_num': None}
    if request.method == 'POST':
        user = request.user
        revi_num = request.POST['revi_num']

        user_obj = models.UserInfo.objects.filter(username=user).first()
        models.Review.objects.filter(revi_num=revi_num).delete()

        ret['user_num'] = user_obj.user_num
        return HttpResponse(json.dumps(ret))


@csrf_exempt
def movietv_comment_reply(request):
    '''
    前端提交表单，ajax传给后台，后台form验证，
    失败返回失败状态，成功则入库，返回数据，由前端拼接HTML，并渲染
    评论:关联发送者，影视
    回复:关联发送者，被回复者，回复于哪些内容（一条评论或另一条回复）
    '''
    ret = {'status': True}
    if request.method == 'POST':
        obj = ReplyForms(request.POST)
        if obj.is_valid():
            reply_content = obj.cleaned_data['reply_content']
            to_user_num = request.POST['to_user_num']
            comment_num = request.POST['comment_num']
            user = request.user

            # 提出评论或是提出回复的人
            from_user_obj = models.UserInfo.objects.filter(username=user).first()

            # 毫秒时间戳
            current_milli_time = lambda: int(round(time.time() * 1000))
            reply_num = str(current_milli_time())[4:-1]

            # 一条回复关联一条评论，同时也可以关联另一条回复（可选非必须）
            if 'reply_num' in request.POST:
                to_reply_num = int(request.POST['reply_num'])
            else:
                to_reply_num = None

            reply_obj = models.ReplyMovieTvComment(reply_content=reply_content,
                                                   with_comment_num_id=comment_num,
                                                   with_reply_num_id=to_reply_num,
                                                   from_user_num_id=from_user_obj.user_num,
                                                   to_user_num_id=int(to_user_num),
                                                   reply_num=reply_num)
            reply_obj.save()

            ret['reply_content'] = reply_obj.reply_content
            ret['from_user_num'] = reply_obj.from_user_num.user_num
            ret['to_user_num'] = reply_obj.to_user_num.user_num

            ret['from_user_name'] = reply_obj.from_user_num.username
            ret['to_user_name'] = reply_obj.to_user_num.username

            ret['reply_num'] = reply_obj.reply_num
            ret['reply_time'] = reply_obj.reply_time
            ret['comm_num'] = reply_obj.with_comment_num_id
            return HttpResponse(json.dumps(ret, default=datetime_handle))
        else:
            ret['status'] = False
            return HttpResponse(json.dumps(ret))


@csrf_exempt
def del_comment_reply(request):
    '''
    删除评论/回复    
    '''
    ret = {'status': True}
    if request.method == 'POST':
        if 'comment_num' in request.POST:
            comment_num = request.POST['comment_num']
            models.MovieTvComment.objects.filter(comm_num=comment_num).delete()
        elif 'reply_num' in request.POST:
            reply_num = request.POST['reply_num']
            models.ReplyMovieTvComment.objects.filter(reply_num=reply_num).delete()
        return HttpResponse(json.dumps(ret))

