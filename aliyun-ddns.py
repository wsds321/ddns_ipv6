
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
import requests
from urllib.request import urlopen
import json


flag = input("请选择开启哪一类DDNS解析（1为IPv4,2为IPv6）：")
accessKeyId=input("输入阿里云accessKeyId：")
accessSecret =input("输入阿里云accessSecret：")
client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')
dnsname = input("输入主域名:")
name=input("输入域名前缀：")

def update(RecordId, RR, Type, Value):  #修改域名解析记录
    from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(RecordId)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    response = client.do_action_with_exception(request)


def add(DomainName, RR, Type, Value):  #添加新的域名解析记录
    from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(DomainName)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)    
    response = client.do_action_with_exception(request)

request = DescribeSubDomainRecordsRequest()
request.set_accept_format('json')
request.set_DomainName(dnsname)
request.set_SubDomain(name + '.' + dnsname)
if flag=="1":
    Typeip="A"
    request.set_Type("A")
    ip = urlopen('https://api-ipv4.ip.sb/ip').read()
    print("获取到IPv4地址：%s" % ip)
if flag=="2":
    Typeip="AAAA"
    request.set_Type("AAAA")
    ip = urlopen('https://api-ipv6.ip.sb/ip').read() 
    print("获取到IP地址：%s" % ip)
ipget = str(ip, encoding='utf-8')
print("获取到IP地址：%s" % ipget)
response = client.do_action_with_exception(request)  #获取域名解析记录列表
domain_list = json.loads(response)  # JSON数据转化
if domain_list['TotalCount'] == 0:
    add(dnsname, name, Typeip, ipget)
    print("新建域名解析")
elif domain_list['TotalCount'] == 1:
    if domain_list['DomainRecords']['Record'][0]['Value'].strip() != ipget.strip():
        update(domain_list['DomainRecords']['Record'][0]['RecordId'], name,Typeip, ipget)
        print("修改域名解析")
    else:  
        print("IP地址没变")
elif domain_list['TotalCount'] > 1:
    from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
    request = DeleteSubDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(dnsname)
    request.set_RR(name)
    request.set_Type(Typeip) 
    response = client.do_action_with_exception(request)
    add(dnsname, name, Typeip, ipget)
    print("修改域名解析成功")


