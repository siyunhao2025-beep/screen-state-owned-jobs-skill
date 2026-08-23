# Skill 发布说明

此目录用于存放可直接导入 WorkBuddy / ChatGPT Skill 系统的发布包说明。

## 为什么不能直接使用 GitHub 的 Download ZIP？

GitHub 的 `Code → Download ZIP` 下载的是完整源码仓库，通常会额外包含仓库根目录，因此可能导致 Skill 导入器无法在第一层找到 `SKILL.md`。

源码仓库结构与 Skill 安装包结构不同：

- GitHub 仓库：用于开发、维护、版本管理；
- Release 安装包：用于用户直接导入 Skill。

## 推荐安装方式

1. 打开 GitHub Releases；
2. 下载对应版本的 `screen-state-owned-jobs-skill-v*.zip`；
3. 不解压，直接上传到 WorkBuddy / ChatGPT 的 Skill 导入窗口。

## 安装包必须包含

```text
SKILL.md
agents/
assets/
references/
scripts/
```

安装包不应包含：

- README.md
- LICENSE
- 用户简历文件
- 运行生成结果
- 开发环境文件

## 版本规划

- v1.0：WorkBuddy/Codex 兼容发布版
- 后续版本：增加自动测试、更多岗位来源接口和用户画像管理能力
