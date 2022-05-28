### 通过代理实时抓取接口，实现再请求

#### 安装依赖

```bash
pip3 install playwright loguru mitmproxy 
playwright install 
```



#### 启动顺序

```bash
mitmdump --mode upstream:http://172.17.0.2:7890 -s mitm_write_file.py
# 你的代理地址和端口（http://172.17.0.2:7890同上）
```

```BASH
mitmdump -p 8088 --mode upstream:http://127.0.0.1:7890 -s mitm_read_file.py
# 你的代理地址和端口（http://172.17.0.2:7890同上）
```

**python3 save_request.py -h**  显示帮助文档

```python
python3 save_request.py -h           (base) 20:00:18

usage: save_request.py [-h] [--is_select_date IS_SELECT_DATE]
                       [--formatdate FORMATDATE] [--source SOURCE]
                       [--target TARGET]

启动抓取接口进程,守护进程

optional arguments:
  -h, --help            show this help message and exit
  --is_select_date IS_SELECT_DATE
                        gnu.py --is_select_date True
                        (是否需要指定日期，默认为不指定，需要抓取指定日期，在参数后边添加 True)
  --formatdate FORMATDATE
                        gnu.py --formatdate 2022-05-29 (指定抓取的日期，不指定默认明天)
  --source SOURCE       gnu.py --source shanghai (指定起点，默认上海)
  --target TARGET       gnu.py --target frankfurt (指定落点，默认法兰克)
```

```bash
python3 save_request.py(等待一分钟左右初始化，会持续抓取，ctrl + c关闭)
```

```bash
python3 input_info_api.py 直接请求用户输入界面，自动输入数据
```

