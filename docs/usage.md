#### 进阶使用

----

#### 自定义配置

自定义配置项可在项目配置文件中配置，以下是默认配置，自定义配置只需要选择需要修改项进行对应配置重置。

```python
# 默认设置
VERSION_LOG = {
    'MD_FILES_DIR': 'version_logs_md',
    'LANGUAGE_POSTFIX_SEPARATION': "_",
    'LANGUAGE_MAPPINGS': {},
    'NAME_PATTERN': '[vV](\d+\.){2,4}md',  # noqa
    'FILE_TIME_FORMAT': '%Y%m%d',
    'LATEST_VERSION_INFORM': False,
    'LATEST_VERSION_INFORM_TYPE': 'redirect',
    'ENTRANCE_URL': 'version_log/',
    'PAGE_HEAD_TITLE': '版本日志',
    'PAGE_STYLE': 'dialog',
    'USE_HASH_URL': True
}
```

- MD_FILES_DIR：版本日志md文件夹，默认情况下会在第一次项目启动时创建version_logs_md文件夹，也可自己创建并把版本日志文件添加进去。如需自定义，请修改文件夹名称并确保自定义文件夹已创建。

- LANGUAGE_POSTFIX_SEPARATION: 多语言版本日志md文件夹后缀分隔符，默认为`_`，如`version_logs_md_en`等。

- LANGUAGE_MAPPINGS：django request 中 LANGUAGE_CODE 和多语言版本日志md文件夹后缀的映射关系，如`{'en': 'en'}`等。
    
      __注意__：多语言版本日志目录只是记录默认语言之外的版本日志的目录，当计算当前最新版本时仍会以 MD_FILES_DIR 目录为准。

- NAME_PATTERN：版本日志文件命名匹配规则，需是正则表达式。（1.3.0 版本之后不做强制校验）

- FILE_TIME_FORMAT: 版本日志文件命名中日期格式，默认为`%Y%m%d`，需为time.strptime支持的格式

- LATEST_VERSION_INFORM：最新版本通知开关

  如果需要开启自动版本通知，除了将该配置设为True，还需要在项目配置文件中添加对应的中间件：

  ```python 
  'version_log.middleware.VersionLogMiddleware'
  ```

  当有新版本日志时，符合以下条件的请求会触发自动版本通知。

    1. 请求方法为GET
    2. 返回页面的Content-Type包含 `text/html`
    3. 返回页面的状态码为200
    4. 请求的用户没被通知过

  通知的方式有两种:

    1. popup，弹窗模式，会在原应用会自动调用show_modal方法
    2. redirect ，页面会被重定向到版本日志页面

  __注意__：开发者功能测试时，添加新版日志文件后需要重启项目进程。基于性能考虑，这里假设正常发布新版本时都会重启项目进程同时添加版本日志文件，所以只会在启动项目时获取一次最新版本号。

- LATEST_VERSION_INFORM_TYPE: 最新版本通知方式(popup/redirect)

- ENTRANCE_URL: version_log模块入口url配置，开发者可自定义一个入口url，用于展示版本日志页面和相关请求，变量为以"/"结尾的字符串。修改这一项的话，需要在本页面对话框的前端配置中将window.version_log_url和在单页面将跳转链接设置为对应的模块入口路径。

- PAGE_HEAD_TITLE：单页面版本日志展示时的标签题目，可以配合开发者网站进行自定义。

- PAGE_STYLE：单页面版本日志的风格选择，默认为对话框单页面，也可改为'gitbook'选择仿gitbook风格单页面。

- USE_HASH_URL: 前端 url 的形式, 默认使用 hash, 类如: /#/index 的路由, 如果是 history 形式,可设置为 False, 获取不到默认为空.

### 自动跳转功能设置

**装饰器控制方式**

通过给视图函数添加装饰器, 在刷新页面或者重新打开页面后,会自动跳转到更新日志查看页面(注意 URL 格式, 默认为 hash, 可设置)

具体设置方法如:

```python
from version_log.decorators import update_log_view

# 访问 / 时会检查用户访问历史版本, 有更新会跳转
@update_log_view
def home(request):
    return render(request, settings.INDEX_TEMPLATE, {})
```
