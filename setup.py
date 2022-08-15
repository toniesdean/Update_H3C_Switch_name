#!/usr/bin/python3
# -*- coding: gbk -*-
# wangxing6674@163.com
# ���̸߳��Ľ���������


import datetime
import threading
import time

import netmiko
import xlrd


class GetDevInfo:  # ��ȡ�豸��¼��Ϣ
    def __init__(self):
        pass

    @staticmethod
    def get_dev_ip():
        data = xlrd.open_workbook(r'./ip_list.xlsx')  # ���ӱ���ȡ·��
        sheet1 = data.sheets()[0]  # ��ȡ��1ҳ��������0��ʼ
        ip_lie = [str(sheet1.cell_value(s, 0)) for s in range(1, sheet1.nrows)]  # ��ȡ��һ�е�IP����,�ӵڶ��п�ʼ
        return ip_lie

    @staticmethod
    def get_dev_username():  # ��ȡ�û�����Ϣ
        data = xlrd.open_workbook(r'./ip_list.xlsx')  # ���ӱ���ȡ·��
        sheet1 = data.sheets()[0]  # ��ȡ��1ҳ��������0��ʼ
        username_lie = [str(sheet1.cell_value(s, 1)) for s in range(1, sheet1.nrows)]  # ��ȡ�ڶ��е��û�������
        return username_lie

    @staticmethod
    def get_dev_password():  # ��ȡ������Ϣ
        data = xlrd.open_workbook(r'./ip_list.xlsx')  # ���ӱ���ȡ·��
        sheet1 = data.sheets()[0]  # ��ȡ��1ҳ��������0��ʼ
        password_lie = [str(sheet1.cell_value(s, 2)) for s in range(1, sheet1.nrows)]  # ��ȡ�����е���������
        return password_lie

    @staticmethod
    def get_commands_list():
        data = xlrd.open_workbook(r'./ip_list.xlsx')  # ���ӱ���ȡ·��
        sheet1 = data.sheets()[0]  # ��ȡ��1ҳ��������0��ʼ
        commands_lie = [str(sheet1.cell_value(s, 3)) for s in range(1, sheet1.nrows)]  # ��ȡ��һ�е�IP����,�ӵڶ��п�ʼ
        return commands_lie


class SSH_Session(GetDevInfo):
    def __init__(self):
        super().__init__()

    now = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))  # ʱ���
    Errordate = time.strftime("%Y-%m-%d", time.localtime(time.time()))  # ���ϱ�����־�����ļ���
    ErrorTime = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))  # ����ʱ��
    switch_with_authentication_issue = []  # �洢��֤ʧ�ܵ��豸
    switch_not_reachable = []  # �洢���ɴ���豸


    @staticmethod
    def ssh_connect(ip, username, password):
        commands = iter(GetDevInfo.get_commands_list())     # ���������
        try:
            ssh = netmiko.ConnectHandler(ip=ip, username=username, password=password, device_type='hp_comware')

            print(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') +
                  '  ���ڽ��룺 ' + ip + '\n')  # ����ɹ�����

            # ssh.send_config_set(Commands_list[0][i], delay_factor=1)  # ��������

            ssh.send_config_set('sysname' + next(commands))  # ���������ļ�

            print(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') +
                  '  ִ����ϣ� ' + ip + '\n')  # �����·��ɹ�����

            return ssh

        except netmiko.exceptions.NetmikoTimeoutException:  # ��ʱ�쳣
            e1 = open(f'.\\log\\{SSH_Session.Errordate}.txt', 'a')  # д����־�ļ���
            print(SSH_Session.ErrorTime, ip, '[Error 1] ���ӳ�ʱ.\n', file=e1)
            SSH_Session.switch_not_reachable.append(ip)
            e1.close()
            return SSH_Session.switch_not_reachable
            pass


        except netmiko.exceptions.NetMikoAuthenticationException:  # ��֤�쳣
            e2 = open(f'.\\log\\{SSH_Session.Errordate}.txt', 'a')
            print(SSH_Session.ErrorTime, ip, '[Error 2] �˻��������.\n', file=e2)
            SSH_Session.switch_with_authentication_issue.append(ip)
            e2.close()
            return SSH_Session.switch_with_authentication_issue
            pass


class Setup(SSH_Session):  # ���߳�ִ����
    def __init__(self):
        super().__init__()

    threads = []  # �̴߳���б�

    @staticmethod
    def setup():  # ִ�з���

        usernames = iter(GetDevInfo.get_dev_username())  # �û���������
        passwords = iter(GetDevInfo.get_dev_password())  # ���������

        for ips in GetDevInfo.get_dev_ip():  # ��������IP,ͬ�������û�������
            username = next(usernames)  # �û���
            password = next(passwords)  # ����
            t = threading.Thread(target=SSH_Session.ssh_connect, args=(ips, username, password))  # �̳߳�
            Setup.threads.append(t)  # �̴߳���б�
            t.start()  # ��ʼ�߳�

        for t in Setup.threads:  # �ȴ��߳̽���
            t.join()


if __name__ == '__main__':
    start_time = time.time()  # ��ʼ��ʱ
    print(f"������ {time.strftime('%X')} ��ʼִ��...\n")
    Setup.setup()
    print(f"������ {time.strftime('%X')} ִ�н���")

    print('\n ===========������===========')

    print('\n������IP���˺Ż��������')
    for count1 in SSH_Session.switch_with_authentication_issue:
        print(count1)

    print('\n������IP���ӳ�ʱ��')
    for count2 in SSH_Session.switch_not_reachable:
        print(count2)

    print(f'\n�ܹ���: %.2fs' % (time.time() - start_time))

    input('\nִ����ϣ���������˳�...')