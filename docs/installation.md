# Skill 安装与发布说明

## 推荐安装方式

不要使用 GitHub 的 `Code → Download ZIP`。

该按钮下载的是完整源码仓库，通常会额外包裹一层仓库目录，不一定符合 WorkBuddy Skill 导入器要求。

推荐流程：

1. 进入 GitHub Releases 页面；
2. 下载 `screen-state-owned-jobs-skill-v1.0.zip`；
3. 保持 ZIP 原样，不解压；
4. 在 WorkBuddy / ChatGPT Skill 导入界面上传。

## Skill 安装包结构

安装包内部必须直接包含：

```
SKILL.md
agents/
assets/
references/
scripts/
```

其中 `SKILL.md` 必须位于第一层。

## 源码仓库与安装包区别

源码仓库用于：

- 开发维护
- 版本控制
- 文档展示
- 贡献协作

Skill 安装包用于：

- WorkBuddy 导入
- ChatGPT Skill 安装
- Codex 环境调用

两者结构不同，不能混用。
