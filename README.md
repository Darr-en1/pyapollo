PyApollo - Python Client for Ctrip's Apollo
================

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

基于Apollo配置中心框架 [Apollo](https://github.com/apolloconfig/apollo) 所开发的Python版本客户端。



Installation
------------
``` shell
pip install strengthen_apollo_client
```

# Features
* 实时同步配置
* 支持yaml,json,json,xml格式


# Usage

- 启动客户端长连接监听

``` python
client = ApolloClient(app_id=<appId>, cluster=<clusterName>, config_server_url=<configServerUrl>)
client.start()
```

- 获取Apollo的配置
  ```
  client.get_value(Key, DefaultValue)
  ```
