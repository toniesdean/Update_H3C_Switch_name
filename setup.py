#!/usr/bin/python3
# -*- coding: gbk -*-
# wangxing6674@163.com
# 单线程更改交换机名称


import datetime
import threading
import time

import netmiko
import xlrd


class GetDevInfo:  # 获取设备登录信息
    def __init__(self):
        pass

    @staticmethod
    def get_dev_ip():
        data = xlrd.open_workbook(r'./ip_list.xlsx')  # 电子表格读取路径
        sheet1 = data.sheets()[0]  # 读取第1页，索引从0开始
        ip_lie = [str(sheet1.cell_value(s, 0)) for s in range(1, sheet1.nrows)]  # 提取第一列的IP数据,从第二行开始
        return ip_lie

    @staticmethod
    def get_dev_username():  # 获取用户名信息
        data = xlrd.open_workbook(r'./ip_list.xlsx')  # 电子表格读取路径
        sheet1 = data.sheets()[0]  # 读取第1页，索引从0开始
        username_lie = [str(sheet1.cell_value(s, 1)) for s in range(1, sheet1.nrows)]  # 提取第二列的用户名数据
        return username_lie

    @staticmethod
    def get_dev_password():  # 获取密码信息
        data = xlrd.open_workbook(r'./ip_list.xlsx')  # 电子表格读取路径
        sheet1 = data.sheets()[0]  # 读取第1页，索引从0开始
        password_lie = [str(sheet1.cell_value(s, 2)) for s in range(1, sheet1.nrows)]  # 提取第三列的密码数据
        return password_lie

    @staticmethod
    def get_commands_list():
        data = xlrd.open_workbook(r'./ip_list.xlsx')  # 电子表格读取路径
        sheet1 = data.sheets()[0]  # 读取第1页，索引从0开始
        commands_lie = [str(sheet1.cell_value(s, 3)) for s in range(1, sheet1.nrows)]  # 提取第一列的IP数据,从第二行开始
        return commands_lie


class SSH_Session(GetDevInfo):
    def __init__(self):
        super().__init__()

    now = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))  # 时间戳
    Errordate = time.strftime("%Y-%m-%d", time.localtime(time.time()))  # 故障报告日志生成文件名
    ErrorTime = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))  # 故障时间
    switch_with_authentication_issue = []  # 存储验证失败的设备
    switch_not_reachable = []  # 存储不可达的设备


    @staticmethod
    def ssh_connect(ip, username, password):
        commands = iter(GetDevInfo.get_commands_list())     # 命令迭代器
        try:
            ssh = netmiko.ConnectHandler(ip=ip, username=username, password=password, device_type='hp_comware')

            print(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') +
                  '  正在接入： ' + ip + '\n')  # 接入成功反馈

            # ssh.send_config_set(Commands_list[0][i], delay_factor=1)  # 发送命令

            ssh.send_config_set('sysname' + next(commands))  # 发送配置文件

            print(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') +
                  '  执行完毕： ' + ip + '\n')  # 命令下发成功反馈

            return ssh

        except netmiko.exceptions.NetmikoTimeoutException:  # 超时异常
            e1 = open(f'.\\log\\{SSH_Session.Errordate}.txt', 'a')  # 写入日志文件名
            print(SSH_Session.ErrorTime, ip, '[Error 1] 连接超时.\n', file=e1)
            SSH_Session.switch_not_reachable.append(ip)
            e1.close()
            return SSH_Session.switch_not_reachable
            pass


        except netmiko.exceptions.NetMikoAuthenticationException:  # 认证异常
            e2 = open(f'.\\log\\{SSH_Session.Errordate}.txt', 'a')
            print(SSH_Session.ErrorTime, ip, '[Error 2] 账户密码错误.\n', file=e2)
            SSH_Session.switch_with_authentication_issue.append(ip)
            e2.close()
            return SSH_Session.switch_with_authentication_issue
            pass


class Setup(SSH_Session):  # 多线程执行类
    def __init__(self):
        super().__init__()

    threads = []  # 线程存放列表

    @staticmethod
    def setup():  # 执行方法

        usernames = iter(GetDevInfo.get_dev_username())  # 用户名迭代器
        passwords = iter(GetDevInfo.get_dev_password())  # 密码迭代器

        for ips in GetDevInfo.get_dev_ip():  # 遍历所有IP,同步迭代用户名密码
            username = next(usernames)  # 用户名
            password = next(passwords)  # 密码
            t = threading.Thread(target=SSH_Session.ssh_connect, args=(ips, username, password))  # 线程池
            Setup.threads.append(t)  # 线程存放列表
            t.start()  # 开始线程

        for t in Setup.threads:  # 等待线程结束
            t.join()


if __name__ == '__main__':
    start_time = time.time()  # 开始计时
    print(f"程序于 {time.strftime('%X')} 开始执行...\n")
    Setup.setup()
    print(f"程序于 {time.strftime('%X')} 执行结束")

    print('\n ===========结果输出===========')

    print('\n·下列IP的账号或密码错误：')
    for count1 in SSH_Session.switch_with_authentication_issue:
        print(count1)

    print('\n·下列IP连接超时：')
    for count2 in SSH_Session.switch_not_reachable:
        print(count2)

    print(f'\n总过程: %.2fs' % (time.time() - start_time))

    input('\n执行完毕，按任意键退出...')