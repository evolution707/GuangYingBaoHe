# -*- coding=utf-8 -*-


class PaginationCustom():
    '''
    自定义分页
    '''
    def __init__(self, pid, total_count, base_url, start, end):
        self.pid = pid
        self.total_count = total_count
        self.base_url = base_url
        self.start = start
        self.end = end

    def get_total_page(self):
        # 第一页默认不显示，即 ''
        if self.pid == '' or self.pid == '0' or self.pid == 0:
            self.pid = 1
        current_page = int(self.pid)
        self.start = (current_page - 1) * 40
        self.end = current_page * 40

        # 传入结果集和结果集总条数，返回总页数  不满一页 总页为一
        total_page, r = divmod(self.total_count, 40)
        if r != 0:
            total_page += 1
        return total_page, current_page

    def get_page_list(self):
        total_page, current_page = self.get_total_page()
        # 显示的页码数
        page_list = []
        # 总页数显示为1 或 数据总条数为0时 ，什么都不显示
        if total_page == 1 or self.total_count == 0:
            return page_list
        else:
            if current_page == 1:
                pass
                # page_list.append("<a href='javascript:void(0);' style='text-decoration:none'><上一页</a>")
            else:
                # 当前页不是第一个，则出现  <
                page_list.append("<a href='/%s/%s'><span class='glyphicon glyphicon-chevron-left' aria-hidden='true'></a>" % (self.base_url, current_page - 1))

            page_start = None
            page_end = None
            if total_page <= 11:
                page_start = 1
                page_end = total_page + 1
            else:
                if current_page <= 6:
                    page_start = 1
                    page_end = 11 + 1
                elif current_page > 6:
                    # 生成首页 和 ...
                    page_list.append("<a href='/%s/%s'>1</a>" % (self.base_url, 1))
                    page_list.append("<a href='javascript:void(0);'>...</a>")

                    if total_page - current_page >= 5:
                        page_start = current_page - 3
                        page_end = current_page + 4
                    else:
                        page_start = total_page - 8
                        page_end = total_page + 1

                    # 接上，最后一页为当前页+6，但不能让他一直+6，当最后一页的页码数大于最大页码数时，让最后一页变成当前页，不再加了
                    if page_end >= total_page:
                        page_end = current_page + 1
                    if current_page + 5 >= total_page:
                        page_end = total_page + 1
                # 根据不同的起始页和终止页生成相应的页码
            for page in range(page_start, page_end):
                # 当前页增加样式

                if page == current_page:
                    page_list.append("<a class='active' href='/%s/%s'>%s</a>" % (self.base_url, page, page))
                else:
                    page_list.append("<a href='/%s/%s'>%s</a>" % (self.base_url, page, page))
            # 生成 ... 和 尾页
            if current_page > 6 and (total_page - current_page >= 6):
                page_list.append("<a href='javascript:void(0);'>...</a>")
                page_list.append("<a href='/%s/%s'>%s</a>" % (self.base_url, total_page, total_page))

            # 如果当前页为总页数，下一页则不再跳转
            if current_page == total_page:
                # page_list.append("<a href='javascript:void(0);' style='text-decoration:none'>下一页></a>")
                pass
            else:
                page_list.append("<a href='/%s/%s'><span class='glyphicon glyphicon-chevron-right' aria-hidden='true'></span></a>" % (self.base_url, current_page + 1))

            page_list = ''.join(page_list)
        return page_list
