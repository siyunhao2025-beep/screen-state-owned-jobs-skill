# Release 发布检查清单

## v1.0 Skill 发布前检查

- [x] Skill 入口位于独立发布目录
- [x] SKILL.md 可被导入器识别
- [x] agents/、assets/、references/、scripts/结构完整
- [x] 源码仓库与安装包分离
- [x] README 已说明不要使用 Code → Download ZIP

## Release 安装包要求

发布文件：

`screen-state-owned-jobs-skill-v1.0.zip`

压缩包第一层必须包含：

```text
SKILL.md
agents/
assets/
references/
scripts/
```

不要包含：

- README.md
- LICENSE
- 用户简历
- 测试输出
- 本地缓存

## 用户测试流程

1. 下载 Release Asset
2. 不解压
3. 导入 WorkBuddy
4. 上传测试简历
5. 验证动态画像与六工作表输出
