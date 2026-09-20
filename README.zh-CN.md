# FaultScribe 中文说明

FaultScribe 是一个本地运行的命令行小工具，用来把开发故障整理成开发者可读的报告。它没有账号、云服务、遥测、付费模型 API，也不会自动上传内容。

当前版本为 `0.1.0` 本地开发候选版：尚未发布到 GitHub 或 PyPI，远程 CI 尚未运行；采用 MIT 许可证。

## 功能

- `doctor`：读取系统、架构以及固定白名单中常用开发工具的版本/缺失状态。只调用版本查询命令，并为每个命令设置超时；不会执行被检查项目的脚本。
- `report`：把你明确选择的问题描述、复现步骤、环境字段和可选的 FaultScribe `doctor` JSON 写为本地 Markdown 与 JSON。
- `redact`：只对你明确指定的一个 UTF-8 文本日志生成独立脱敏副本，可在终端预览；原文件不会被覆盖或修改。

默认不会自动采集源代码、环境变量、Git remote、邮箱、真实用户名或完整绝对路径。请不要把敏感信息写入 `report` 的输入，分享前请自行检查结果。

## 安装与示例

需要 Python 3.9 或更高版本：

```sh
python3 -m pip install .
faultscribe --help
```

可复现的合成示例和所有命令参数见英文 [README](README.md)。示例只在本地创建合成文件，绝不会上传或提交报告。

```text
faultscribe doctor [--timeout 秒数] [--output 文件]
faultscribe report --title 标题 --description 文件 [--steps 文件]
                  [--environment 键=值] [--doctor-json 文件]
                  [--output-dir 目录] [--name 文件名前缀]
faultscribe redact 输入日志 [--output 输出文件] [--preview]
```

输出文件默认拒绝覆盖。非 UTF-8 文本、损坏 JSON、空的环境键以及把脱敏输出指定为原文件都会报错，而不会写报告或覆盖原始日志。

## 脱敏边界

内置规则会尝试匹配常见的邮箱、密钥/令牌、`password=` 等赋值和本地用户路径。这只是辅助筛选，不能保证不会泄露：不常见格式、编码内容、压缩包、截图、未来格式以及无上下文的随机字符串都可能漏检；普通文本也可能误报。每次 `redact` 都会显示这项警告。对外分享前必须人工复核。

请阅读 [SECURITY.md](SECURITY.md)、[CONTRIBUTING.md](CONTRIBUTING.md) 与 [CHANGELOG.md](CHANGELOG.md)。
