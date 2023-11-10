# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import functools

from django.shortcuts import render
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from version_log import config
from version_log.models import VersionLogVisited
from version_log.utils import get_version_list, get_parsed_html, get_parsed_markdown_file_path, \
    get_md_files_dir_with_language_code

logger = logging.getLogger(__name__)


def latest_read_record(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        visit_log_version = request.GET.get("log_version") or request.POST.get(
            "log_version"
        )
        if config.LATEST_VERSION_INFORM and visit_log_version == config.LATEST_VERSION:
            VersionLogVisited.objects.update_visit_version(
                request.user.username, visit_log_version
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def version_logs_page(request):
    """版本日志页面"""
    version_list = get_version_list()
    if version_list is None:
        logger.error(
            "MD_FILES_DIR not found. Current path is {}".format(config.MD_FILES_DIR)
        )
        version_list = []  # 用无日志文件提示对用户屏蔽错误
    else:
        version_list = [
            {"version": version, "date": date} for (version, date) in version_list
        ]
    context = {
        "version_list": version_list,
        "page_title": config.PAGE_HEAD_TITLE,
        "ENTRANCE_URL": config.ENTRANCE_URL,
        "USE_HASH_URL": config.USE_HASH_URL,
    }
    if config.PAGE_STYLE == "dialog":
        return render(request, "version_log/version_logs_dialog_page.html", context)
    else:
        return render(request, "version_log/version_logs_page.html", context)


def version_logs_block(request):
    """版本日志数据块"""
    return render(request, "version_log/version_logs_block.html")


def version_logs_list(request):
    """获取版本日志列表"""
    language_code = getattr(request, "LANGUAGE_CODE", None)
    version_list = get_version_list(language_code)
    if version_list is None:
        md_files_dir = get_md_files_dir_with_language_code(language_code)
        logger.error(
            "MD_FILES_DIR not found. Current path is {}".format(md_files_dir)
        )
        return JsonResponse(
            {"result": False, "code": -1, "message": _("访问出错，请联系管理员。"), "data": None}
        )
    response = {
        "result": True,
        "code": 0,
        "message": _("日志列表获取成功"),
        "data": version_list,
    }
    return JsonResponse(response)


def handle_version_content(version: str, log_format: str, language_code) -> str:
    """处理内容"""
    if log_format == "html":
        html_text = get_parsed_html(version, language_code) or ""
        return html_text
    elif log_format == "md":
        markdown_file_path = get_parsed_markdown_file_path(version, language_code)
        with open(markdown_file_path, "r", encoding="utf-8") as markdown_handler:
            return markdown_handler.read()
    else:
        return ''


@latest_read_record
def version_logs_list_with_detail(request):
    """获取包含详情的日志列表"""
    language_code = getattr(request, "LANGUAGE_CODE", None)
    log_format = request.GET.get("log_format", "md")

    version_list = []
    try:
        for data_list in get_version_list(language_code):
            version = data_list[0]
            version_list.append({
                "version": version,
                "time": data_list[1],
                "content": handle_version_content(version, log_format, language_code)
            })
    except:
        md_files_dir = get_md_files_dir_with_language_code(language_code)
        logger.error(
            "MD_FILES_DIR not found. Current path is {}".format(md_files_dir)
        )
        return JsonResponse(
            {"result": False, "code": -1, "message": _("访问出错，请联系管理员。"), "data": None}
        )

    response = {
        "result": True,
        "code": 0,
        "message": _("日志详情列表获取成功"),
        "data": version_list,
    }
    return JsonResponse(response)


@latest_read_record
def get_markdown_version_log_detail(request):
    """
    获取单条版本日志，不转换markdown格式
    """
    language_code = getattr(request, "LANGUAGE_CODE", None)
    log_version = request.GET.get("log_version")
    markdown_file_path = get_parsed_markdown_file_path(log_version, language_code)
    with open(markdown_file_path, 'r', encoding="utf-8") as markdown_handler:
        markdown_text = markdown_handler.read()
    response = {"result": True, "code": 0, "message": _("Markdown格式日志详情获取成功"), "data": markdown_text}
    return JsonResponse(response)


@latest_read_record
def get_version_log_detail(request):
    """获取单条版本日志转换结果"""
    language_code = getattr(request, "LANGUAGE_CODE", None)
    log_version = request.GET.get("log_version")
    html_text = get_parsed_html(log_version, language_code)
    if html_text is None:
        logger.error(
            "md file not found or log version not valid. Log version is {}".format(
                log_version
            )
        )
        response = {
            "result": False,
            "code": -1,
            "message": _("日志版本文件没找到，请联系管理员"),
            "data": None,
        }
        return JsonResponse(response)
    response = {"result": True, "code": 0, "message": _("日志详情获取成功"), "data": html_text}
    return JsonResponse(response)


def has_user_read_latest(request):
    """查询当前用户是否看过最新版本日志"""
    username = request.user.username
    has_latest_read = VersionLogVisited.objects.has_visit_latest(
        username, config.LATEST_VERSION
    )
    return JsonResponse(
        {
            "result": True,
            "code": 0,
            "message": "",
            "data": {
                "latest_version": config.LATEST_VERSION,
                "has_read_latest": has_latest_read,
            },
        }
    )
