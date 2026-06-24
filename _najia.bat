@echo off
setlocal

:: 在这里定义你要执行的命令，后续修改只需要改这一行
set "CMD_TO_RUN=python -m najia.gui"

:: 自动显示即将执行的指令
echo ******************************
echo 执行指令: %CMD_TO_RUN%
echo ******************************
echo.

:: 调用 PowerShell 运行变量中的命令
powershell -Command "%CMD_TO_RUN%"

endlocal