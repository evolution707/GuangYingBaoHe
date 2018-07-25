# -*- coding: utf-8 -*-
from django.db import models
from django.urls import reverse
from django.db.models import permalink
from django.contrib.auth.models import AbstractUser


class MovieAndTv(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True, verbose_name='片名')
    director = models.CharField(max_length=255, verbose_name='导演', null=True, blank=True)
    writer = models.CharField(max_length=255, verbose_name='编剧', null=True, blank=True)
    actor = models.CharField(max_length=255, verbose_name='主演', null=True, blank=True)
    grade = models.CharField(max_length=10, verbose_name='评分', null=True, blank=True)
    language = models.CharField(max_length=32, verbose_name='语言', null=True, blank=True)
    other_name = models.CharField(max_length=255, verbose_name='又名', null=True, blank=True)
    intro = models.TextField(verbose_name='简介', null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True, blank=True)
    cd = models.CharField(max_length=32, verbose_name='集数', null=True, blank=True)
    min = models.CharField(max_length=32, verbose_name='单集片长', null=True, blank=True)
    lenght = models.CharField(max_length=32, verbose_name='片长', null=True, blank=True)
    release_date = models.CharField(max_length=60, verbose_name='上映日期', null=True, blank=True)
    debut = models.CharField(max_length=32, verbose_name='首播', null=True, blank=True)
    pic_url = models.CharField(max_length=255, verbose_name='图片链接', null=True, blank=True)
    pic_num = models.CharField(max_length=255, verbose_name='图片编号', null=True, blank=True)
    area = models.CharField(max_length=80, verbose_name='制片国家/地区', null=True, blank=True)
    type = models.CharField(max_length=100, verbose_name='类型', null=True, blank=True)
    num = models.IntegerField(verbose_name='编号', null=True, blank=True, unique=True)
    torrent_title = models.TextField(verbose_name='种子标题', null=True, blank=True)
    torrent = models.TextField(verbose_name='种子',null=True, blank=True)

    m_to_area = models.ManyToManyField('MovieAndTvArea', verbose_name='制片管家/地区选择')
    m_to_type = models.ManyToManyField('MovieAndTvType', verbose_name='类型选择')
    f_to_time = models.ForeignKey('MovieAndTvTime', verbose_name='年代选择', null=True, blank=True, on_delete=models.CASCADE)
    f_to_category = models.ForeignKey('MovieOrTv', verbose_name='类别选择', null=True, blank=True, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = "影视信息"
        verbose_name_plural = '影视信息'


class MovieAndTvType(models.Model):
    id = models.AutoField(primary_key=True)
    type_choices = ((1, '剧情'), (2, '喜剧'), (3, '动作'), (4, '爱情'), (5, '科幻'), (6, '悬疑'), (7, '惊悚'),
                    (8, '恐怖'), (9, '犯罪'), (10, '同性'), (11, '音乐'), (12, '歌舞'), (13, '传记'), (14,'历史'),
                    (15, '战争'), (16, '西部'), (17, '奇幻'), (18, '冒险'), (19, '灾难'), (20, '武侠'), (21, '情色'), (22, '纪录片'))
    type = models.CharField(max_length=32, choices=type_choices, verbose_name='类型', null=True, blank=True)

    def __unicode__(self):
        return "{0}".format(self.type)

    class Meta:
        verbose_name = "影视类型"
        verbose_name_plural = '影视类型'


class MovieAndTvArea(models.Model):
    id = models.AutoField(primary_key=True)
    area_choices = ((1, '中国大陆'), (2, '美国'), (3, '香港'), (4, '台湾'), (5, '日本'), (6, '韩国'), (7, '英国'),
                   (8, '法国'), (9, '德国'), (10, '意大利'), (11, '西班牙'), (12, '印度'), (13, '泰国'), (14, '俄罗斯'),
                   (15, '伊朗'), (16, '加拿大'), (17, '澳大利亚'), (18, '爱尔兰'), (19, '瑞典'), (20, '巴西'), (21, '丹麦'), (22, '其他'))
    area = models.CharField(max_length=32, choices=area_choices, verbose_name='制片国家/地区', null=True, blank=True)

    def __unicode__(self):
        return "{0}".format(self.area)

    class Meta:
        verbose_name = "制片国家/地区"
        verbose_name_plural = '制片国家/地区'


class MovieAndTvTime(models.Model):
    id = models.AutoField(primary_key=True)
    time_choices = ((1, '2018'), (2, '2017'), (3, '2016'), (4, '2015'),
                    (5, '2014'), (6, '2013'), (7, '2012'), (8, '2011'),
                    (9, '2000-2010'), (10, '90年代'), (11, '80年代'), (12, '更早'))
    time = models.CharField(max_length=32, choices=time_choices, verbose_name='年代', null=True, blank=True)

    def __unicode__(self):
        return "{0}".format(self.time)

    class Meta:
        verbose_name = '年代'
        verbose_name_plural = '年代'


class MovieOrTv(models.Model):
    id = models.AutoField(primary_key=True)
    category_choices = ((1, '电影'), (2, '电视剧'))
    category = models.CharField(max_length=10, choices=category_choices, verbose_name='类别', null=True, blank=True)

    def __unicode__(self):
        return "{0}".format(self.category)

    class Meta:
        verbose_name = '类别'
        verbose_name_plural = '类别'


class UserInfo(AbstractUser):
    user_num = models.IntegerField(verbose_name='用户编号', unique=True, null=True, blank=True)
    email = models.EmailField(verbose_name='邮箱', unique=True, blank=True, null=True)
    head_img = models.ImageField(max_length=32, verbose_name='头像', null=True, blank=True, upload_to='upload/head/', default='upload/head/defalut_head.jpg')
    self_intro = models.CharField(max_length=255, verbose_name='自我介绍', null=True, blank=True)

    def __unicode__(self):
        return "{0}".format(self.username)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = '用户信息'


class Collect(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    coll_user = models.ForeignKey('UserInfo', on_delete=models.CASCADE, related_name='user_has_collect')
    coll_movietv = models.ForeignKey('MovieAndTv', on_delete=models.CASCADE, related_name='movietv_has_collect')

    def __unicode__(self):
        return '%s'%self.id
    class Meta:
        verbose_name = "收藏"
        verbose_name_plural = '收藏'


class Review(models.Model):
    '''
    影评
    通过django-guardian设置权限
    '''
    revi_num = models.IntegerField(verbose_name='编号', null=True, blank=True, unique=True)
    revi_title = models.CharField(max_length=255, unique=True, verbose_name='标题')
    revi_content = models.TextField(verbose_name='内容')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    revi_utime = models.DateTimeField(auto_now=True, verbose_name='更新时间', null=True)
    revi_image = models.ImageField(upload_to='upload/revi/', verbose_name='图片', null=True, blank=True)
    revi_user = models.ForeignKey(UserInfo, verbose_name='作者', on_delete=models.CASCADE, related_name='user_has_revi')
    revi_movietv = models.ForeignKey(MovieAndTv, verbose_name='关联影视', on_delete=models.CASCADE, related_name='movietv_has_revi')
    revi_views = models.PositiveIntegerField(default=0)


    def __unicode__(self):
        return self.revi_title

    def increate_views(self):
        self.revi_views += 1
        self.save(update_fields=['revi_views'])



    class Meta:
        verbose_name = "影评"
        verbose_name_plural = '影评'


class Vote(models.Model):
    vote_ctime = models.DateTimeField(auto_now_add=True, null=True)
    vote_user = models.ForeignKey(UserInfo, verbose_name='关联用户', on_delete=models.CASCADE, related_name='user_has_vote')
    vote_revi = models.ForeignKey(Review, verbose_name='关联影评', on_delete=models.CASCADE, related_name='revi_has_vote')

    def __unicode__(self):
        return '%s'%self.id

    class Meta:
        verbose_name = "点赞"
        verbose_name_plural = '点赞'


# class Views(models.Model):
#
#     views_revi = models.ForeignKey(Review, verbose_name='阅读量', on_delete=models.CASCADE)
#
#     def __unicode__(self):
#         return '%s'%self.id
#
#     class Meta:
#         verbose_name = "阅读量"
#         verbose_name_plural = '阅读量'


class MovieTvComment(models.Model):
    '''
    对影视的评论
    '''
    m_content = models.TextField(verbose_name='影视评论', null=True, blank=True)
    comm_num = models.IntegerField(verbose_name='评论编号', unique=True, null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True, blank=True)
    comm_movietv_num = models.ForeignKey(MovieAndTv, to_field='num', on_delete=models.CASCADE, related_name='movietv_has_comment')
    comm_user_num = models.ForeignKey(UserInfo, to_field='user_num', on_delete=models.CASCADE, related_name='user_has_comment')

    def __unicode__(self):
        return self.m_content

    class Meta:
        verbose_name = "影视评论"
        verbose_name_plural = '影视评论'


class ReplyMovieTvComment(models.Model):
    '''
    回复 ，属于哪个评论下的回复，谁的回复，回复了谁
    '''
    reply_content = models.TextField(verbose_name='回复', null=True, blank=True)
    reply_time = models.DateTimeField(auto_now_add=True, verbose_name='回复时间', null=True, blank=True)
    reply_num = models.IntegerField(verbose_name='回复编号', unique=True, null=True, blank=True)
    with_comment_num = models.ForeignKey(MovieTvComment, to_field='comm_num', on_delete=models.CASCADE, related_name='comment_has_reply', null=True, blank=True)
    with_reply_num = models.ForeignKey('self', to_field='reply_num', on_delete=models.CASCADE, related_name='reply_has_reply', null=True, blank=True)
    from_user_num = models.ForeignKey(UserInfo, to_field='user_num', on_delete=models.CASCADE, related_name='reply_from_user')
    to_user_num = models.ForeignKey(UserInfo, to_field='user_num', on_delete=models.CASCADE, related_name='reply_to_user', null=True, blank=True)

    def __unicode__(self):
        return self.reply_content

    class Meta:
        verbose_name = "评论回复"
        verbose_name_plural = '评论回复'


class ReviComment(models.Model):
    '''
    对影评的评论
    '''
    r_content = models.TextField(verbose_name='影评评论', null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True, blank=True)
    comm_revi_num = models.ForeignKey(Review, to_field='revi_num', on_delete=models.CASCADE, related_name='revi_has_comment')
    comm_user_num = models.ForeignKey(UserInfo, to_field='user_num', on_delete=models.CASCADE, related_name='u_has_comment')

    def __unicode__(self):
        return self.r_content

    class Meta:
        verbose_name = "影评评论"
        verbose_name_plural = '影评评论'