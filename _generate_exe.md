- [pyinstaller踩坑记，缺少依赖、打包错误或运行无效排查过程备忘](https://zhuanlan.zhihu.com/p/354609842)
- [Pyinstaller 打包发布经验总结](https://blog.csdn.net/weixin_42052836/article/details/82315118)

prepare the `version.txt` `user.ico`

Enter into code dir and using

```
.\venv\Scripts\activate
```


check pyinstaller version
```
.\venv\Scripts\python.exe .\venv\Scripts\pyinstaller.exe -v
6.4
```
in the terminal and
run:

```bash
.\venv\Scripts\python.exe .\venv\Scripts\pyinstaller.exe --clean --windowed --icon=next.ico --name najiachart --collect-all najia --add-data "./najia/data;najia/data" run_gui.py

# 测试用
.\venv\Scripts\python.exe .\venv\Scripts\pyinstaller.exe --clean --icon=next.ico --name najiachart --collect-all najia --add-data "./najia/data;najia/data" run_gui.py
```

