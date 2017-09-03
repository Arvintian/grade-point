#!/usr/bin/python
# coding=utf8

import urllib2
import urllib
import threading
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def one_person(school_num):
    file = open(school_num+".txt","w")
    file.write("========================================================================================================\n")
    req = urllib2.Request("http://210.44.176.116/cjcx/zcjcx_list.php")
    data = {
        "post_xuehao":school_num,
    }
    req.add_data(urllib.urlencode(data))
    ret = urllib2.urlopen(req)
    ret = ret.read()
    #/html/body/table/tr[5]/td/table/tr
    html_tree = etree.HTML(ret)
    name_node = html_tree.xpath("/html/body/table/tr[1]/td/table/tr[2]/td[2]")
    course = html_tree.xpath("/html/body/table/tr[5]/td/table/tr")
    course_list = []
    for item_tr in course[1:]:
        c_type = item_tr.xpath("td[4]")
        c_name = item_tr.xpath("td[6]")
        c_sorce = item_tr.xpath("td[8]")
        is_two = item_tr.xpath("td[9]")
        c_res = item_tr.xpath("td[10]")
        c_res_again = item_tr.xpath("td[11]")
        #过滤共选课
        if c_type[0].text.strip() == u"公选课":
            file.write("跳过：公修课"+c_name[0].text+"\n")
            continue
        if is_two[0].text.strip() != u"":
            file.write("跳过：第二专业"+c_name[0].text+"\n")
            continue
        c_res = c_res[0].text.strip()
        if c_res == u"缓考":
            c_res = c_res_again[0].text.strip()
        #等级制成绩
        if c_res == u"优秀":
            c_res = 95
        elif c_res == u"良好":
            c_res = 84
        elif c_res == u"中等":
            c_res = 73
        elif c_res == u"及格":
            c_res = 62
        elif c_res == u"不及格":
            c_res = 0
        elif c_res == u"合格":
            c_res = 70
        elif c_res == u"不合格":
            c_res = 0
        elif c_res == u"免修":
            c_res = 73
        else :
            #尝试浮点数成绩
            try :
                c_res = float(c_res)
            except Exception:
            #其他未知情况
                c_res = u"0"
        c_res_again = c_res_again[0].text.strip()
        if c_res_again == u"优秀":
            c_res_again = 95
        elif c_res_again == u"良好":
            c_res_again = 84
        elif c_res_again == u"中等":
            c_res_again = 73
        elif c_res_again == u"及格":
            c_res_again = 62
        elif c_res_again == u"不及格":
            c_res_again = 0
        elif c_res_again == u"合格":
            c_res_again = 70
        elif c_res_again == u"不合格":
            c_res_again = 0
        elif c_res_again == u"免修":
            c_res_again = 73
        else:
            try :
                c_res_again = float(c_res_again)
            except Exception:
                c_res_again = u"0"
        item_course = {
            "type":c_type[0].text.strip(),
            "name":c_name[0].text.strip(),
            "sorce":float(c_sorce[0].text.strip()),
            "res":float(c_res),
            "res_again":float(c_res_again),
        }
        course_list.append(item_course)

    sum_sorce = 0.0
    sum_res = 0.0
    #课程集合
    course_set = set()
    #倒着算,处理重修情况,只算最后一次该课程修的情况，之前的跳过
    course_list.reverse()
    for item in course_list:
        if item['name'] not in course_set:
            course_set.add(item["name"])
            sum_sorce += item["sorce"]
            if item['res'] >= 60:
                # 正考通过
                sum_res += item["sorce"] * item["res"]
                file.write("计算-正："+item["type"]+item["name"]+"学分-"+str(item["sorce"])+"实际成绩-"+str(item["res"])+"计算成绩-"+str(item["res"])+"\n")
            else:
                # 补考
                if item['res_again']>=60:
                    #sum_res += item["sorce"] * item["res_again"]
                    sum_res += item["sorce"] * 60.0
                    file.write("计算-补："+item["type"]+item["name"]+"学分-"+str(item["sorce"])+"实际补考成绩-"+str(item["res_again"])+"计算成绩-"+"60.0"+"\n")
                else:
                    #补考没过
                    sum_res += 0
                    #打印计算的课程
                    file.write("计算-补："+item["type"]+item["name"]+"学分-"+str(item["sorce"])+"实际补考成绩-"+str(item["res_again"])+"计算成绩-"+"0.0"+"\n")
        else:
            file.write("跳过(已重修)："+item["type"]+item["name"]+str(item["sorce"])+"正考-"+str(item["res"])+"补考-"+str(item["res_again"])+"\n")
            continue
    file.write("课程数："+str(len(course_set))+"\n")
    file.write("总学分："+str(sum_sorce)+"\n")
    file.write("总绩点："+str(sum_res)+"\n")
    file.write("姓名："+str(name_node[0].text)+"\n")
    file.write("绩点："+str(sum_res/sum_sorce)+"\n")
    file.write("========================================================================================================\n")
    file.close()

if __name__=="__main__":
    school_num = raw_input("请输入学号:").strip()
    one_person(school_num)
    print "计算完成，结果查阅{}.txt".format(school_num)
