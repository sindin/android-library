#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author  : Hu Ji
@file    : utils.py
@time    : 2018/11/25
@site    :
@software: PyCharm

              ,----------------,              ,---------,
         ,-----------------------,          ,"        ,"|
       ,"                      ,"|        ,"        ,"  |
      +-----------------------+  |      ,"        ,"    |
      |  .-----------------.  |  |     +---------+      |
      |  |                 |  |  |     | -==----'|      |
      |  | $ sudo rm -rf / |  |  |     |         |      |
      |  |                 |  |  |/----|`---=    |      |
      |  |                 |  |  |   ,/|==== ooo |      ;
      |  |                 |  |  |  // |(((( [33]|    ,"
      |  `-----------------'  |," .;'| |((((     |  ,"
      +-----------------------+  ;;  | |         |,"
         /_)______________(_/  //'   | +---------+
    ___________________________/___  `,
   /  oooooooooooooooo  .o.  oooo /,   \,"-----------
  / ==ooooooooooooooo==.o.  ooo= //   ,`\--{)B     ,"
 /_==__==========__==_ooo__ooo=_/'   /___________,"
"""

import os
import re
import subprocess
import warnings
from collections import Iterable
from urllib.request import urlopen

import requests
from tqdm import tqdm, TqdmSynchronisationWarning


class _process(subprocess.Popen):

    def __init__(self, command, stdin, stdout, stderr):
        """
        :param command: 命令
        :param stdin: 输入流
        :param stdout: 输出流
        :param stderr: 错误输出流
        """
        self.out = ""
        self.err = ""
        self.returncode = -0x7fffffff
        subprocess.Popen.__init__(self, command, shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

    def communicate(self, **kwargs):
        out, err = None, None
        try:
            out, err = subprocess.Popen.communicate(self, **kwargs)
            if out is not None:
                self.out = self.out + out.decode(errors='ignore')
            if err is not None:
                self.err = self.err + err.decode(errors='ignore')
            return out, err
        except Exception as e:
            self.err = self.err + str(e)
        return out, err


class utils:

    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT

    @staticmethod
    def int(obj: object, default: int = 0) -> int:
        """
        转为int
        :param obj: 需要转换的值
        :param default: 默认值
        :return: 转换后的值
        """
        try:
            # noinspection PyTypeChecker
            return int(obj)
        except:
            return default

    @staticmethod
    def bool(obj: object, default: bool = False) -> bool:
        """
        转为bool
        :param obj: 需要转换的值
        :param default: 默认值
        :return: 转换后的值
        """
        try:
            return bool(obj)
        except:
            return default

    @staticmethod
    def findall(string: str, reg: str) -> [str]:
        """
        找到所有匹配的子串
        :param string: 字符串
        :param reg: 子串（正则表达式）
        :return: 匹配的子串
        """
        return re.compile(reg).findall(string)

    @staticmethod
    def replace(string: str, reg: str, val: str, count=0) -> str:
        """
        替换子串
        :param string: 字符串
        :param reg: 子串（正则表达式）
        :param val: 替换的值
        :param count: 替换次数，为0替换所有
        :return: 替换后的值
        """
        return re.sub(reg, val, string, count=count)

    @staticmethod
    def match(string: str, reg: str) -> bool:
        """
        是否匹配子串
        :param string: 字符串
        :param reg: 子串（正则表达式）
        :return: 是否包含
        """
        return re.search(reg, string) is not None

    @staticmethod
    def contain(obj: object, key: object, value: object = None) -> bool:
        """
        是否包含内容
        :param obj: 对象
        :param key: 键
        :param value: 值
        :return: 是否包含
        """
        if object is None:
            return False
        if isinstance(obj, dict):
            return key in obj and (value is None or obj[key] == value)
        if isinstance(obj, Iterable):
            return key in obj
        return False

    @staticmethod
    def is_empty(obj: object):
        """
        对象是否为空
        :param obj: 对象
        :return: 是否为空
        """
        if obj is None:
            return True
        if isinstance(obj, Iterable):
            # noinspection PyTypeChecker
            return obj is None or len(obj) == 0
        return False

    @staticmethod
    def exec(command: str, stdin=PIPE, stdout=PIPE, stderr=PIPE) -> _process:
        """
        执行命令
        :param command: 命令
        :param stdin: 输入流，默认为utils.PIPE，标准输入为None
        :param stdout: 输出流，默认为utils.PIPE，标准输出为None
        :param stderr: 错误输出流，默认为utils.PIPE，输出到输出流为utils.STDOUT，标准输出为None
        :return: 子进程
        """
        process = _process(command, stdin, stdout, stderr)
        process.communicate()
        return process

    @staticmethod
    def download(url: str, path: str) -> int:
        """
        从指定url下载文件
        :param url: 下载链接
        :param path: 保存路径
        :return: 文件大小
        """
        file_dir = os.path.dirname(path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        if os.path.exists(path):
            first_byte = os.path.getsize(path)
        else:
            first_byte = 0
        file_size = int(urlopen(url).info().get('Content-Length', -1))
        if first_byte >= file_size:
            return file_size
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", TqdmSynchronisationWarning)
            pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=url.split('/')[-1])
            req = requests.get(url, headers=header, stream=True)
            with (open(path, 'ab')) as f:
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        pbar.update(1024)
                    pass
                pass
            pbar.close()
        return file_size
