# pairwise-depth-prepass-alpha

## 领域

游戏、图形与多媒体

## 主题

深度预通道与 alpha

## 说明

预通道与基础通道的 alpha、位移与深度精度一致。

初始状态下 `render/depth_prepass_alpha.py` 中所有函数抛出 `NotImplementedError`，测试全部失败。
修复实现后运行：

```bash
python -m pytest -q
```

期望全部通过。
