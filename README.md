# 系统监控自动报警

## 部署方法

### 安装依赖

    pip install -r requirement.txt

复制 `config.py.example` 为 `config.py`, 修改配置此文件中对应的项.

准备部署环境

    python manager.py deploy

### 运行

以 gunicorn 运行

    gunicorn -c gun.conf manage:app

### HTTP API

发送警报

    URI: /api/alarm/

    方式: POST JSON body

    HTTP Header 需要加上 X-CSRFToken

    Body 参数形如

        {
            "token": "ffffffffffffffffffffffffffffffff",
            "title": "Something Wrong",
            "text": "This is just another alarm",
            "emails": ["somebody@example.org", "anothor@example.orz"]
        }

    其中 X-CSRFToken 的取值与 token 是登陆创建 app 后, 该 app 的 token; 成功返回状态码是 201

获取 DSN

    URI: /api/dsn/<user_name>/<project_name>/

    方式: GET

    URI 参数:

        user_name : 用户名
        project_name : 项目名

    返回值为 JSON

    {
        "dsn": DSN 地址
    }
