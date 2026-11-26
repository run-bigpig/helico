# 创作自己的宠物

把喜欢的角色做成陪你工作的宠物，可以自己绘制，也可以请图像生成工具协助。宠物需要一套动作图集和配准参数，走路、跳跃、眨眼及鼠标互动由袖蝶 Helico 提供。

设置页从袖蝶 Helico 的公开目录发现和安装社区宠物。开发版可以从独立目录预览资源包。你可以复制这份指南，让智能体协助整理素材与配置。[公开目录](https://github.com/run-bigpig/helico/blob/main/catalog-v2.json)

## 1. 设计角色与素材

先画一张完整的角色参考图，再据此制作各个动作。所有帧保持同一造型、比例、配色和材质，默认朝右；转身由应用镜像完成。建议头身分明、双眼清楚，手脚与身体容易区分，方便配准和动画。

图片使用透明背景的静态 WebP，不能用动图。角色、触角和四肢要完整放在各自单格内，留出边缘空间；不画文字、网格线或背景。站姿与步态保持一致的脚底基线，步态按接触、支撑、离地、回摆连续衔接。

| 文件 | 像素尺寸 | 内容 |
|---|---|---|
| `poses.webp` | 1024 × 1024 | 4 列 × 4 行，每格 256 × 256，排列见下表 |
| `walk.webp` | 1024 × 768 | 4 列 × 3 行，按行读取的 12 帧连续步态，每格 256 × 256 |
| `face.webp` | 288 × 80 | 3 列 × 1 行，每列 96 × 80，供动态眼睛覆盖原眼睛时填补面部材质 |

`poses.webp` 从左到右、从上到下排列：

| 行 | 第 1 格 | 第 2 格 | 第 3 格 | 第 4 格 |
|---|---|---|---|---|
| 1 | 站立 idle | 等待 waiting | 工作 running | 查看 review |
| 2 | 失落 failed | 挥手 waving | 跳跃 jumping | 坐下 sit |
| 3 | 打盹 nap | 攀附 hang | 保留格 | 冲刺 sprint |
| 4 | 旧步态 1 | 旧步态 2 | 旧步态 3 | 旧步态 4 |

当前行走读取独立的 `walk.webp`；探头复用站姿头部。保留格及旧步态格可沿用参考资源的排列。

可选的工作打字姿势需要同时准备 `typing.webp` 和 `typing-base.webp`（均为 512 × 512）及 `rig.typing`。前者是坐在电脑前、双手落键的完整姿势，后者移除双臂并补全身体和键盘；缺少任一项都会校验失败。首次制作可以先完成基础三图。

## 2. 配准头部、眼睛和步态

解压「袖蝶 · 青翎」资源包，以其中 `manifest.json` 的 `rig` 为参考。替换图集后，按新图片重新测量配准坐标。[青翎资源包](https://github.com/run-bigpig/helico/releases/tag/helico-jade-v1.0.0)

配准坐标以 **256 × 256 单格**为基准，原点在左上，x 向右、y 向下；512px 的打字图也使用这一坐标基准。

| 配置 | 需要填写什么 |
|---|---|
| `layout.head` | 站姿中含触角的头部矩形：left、top、right、bottom |
| `layout.idleNeck` / `idleFloor` | 站姿的颈部连接点与脚底高度 |
| `layout.walkNecks` / `walkFloor` | 12 个步态帧各自的颈部连接点，以及步态的共同脚底高度 |
| `faces` | 至少提供 idle 的颈部位置；按各姿势填写眼睛中心、半径、角度及局部材质明暗修正；闭眼姿势可不提供眼睛 |
| `eyes` | 眼睛样式 textured（保留原虹膜）、stitched（绣眼）或 ink（漫画），以及配色、面部材质列号和取样偏移 |
| `armEdge` | 手臂裁切边界，0–100 的百分比 |
| 可选 `typing` | 姿势垂直偏移 offsetY、整体缩放 scale（可省略，默认 1，以画布底部中央为支点）、一轮打字时间 cycleMs，以及两只手臂的裁切路径 clip、肩部支点 pivot、抬手角度 lift |

坐标范围为 0–256，颈部需在脚底上方，头部矩形需有正宽高；`walkNecks` 必须恰好 12 项。完整字段和取值范围以 Format 1 定义（`packages/protocol/src/pet.ts`） 为准。

## 3. 构建资源包

把图集和 `manifest.json` 放在同一目录。在清单中填写新的 `id`、`version`、双语名称和描述，再更新 `rig`。使用 Python 3 和 Pillow 运行袖蝶打包脚本。[打包脚本](https://github.com/run-bigpig/helico/blob/main/build/pet-art/package_pet.py)

```sh
python3 -m pip install Pillow
python3 build/pet-art/package_pet.py ./my-pet ./pet-release
```

脚本重新计算清单内的大小和 SHA-256，从站姿生成预览，并把 ZIP、预览和单条目的 `catalog-v2.json` 写入 `pet-release/`。如果使用自己的 GitHub 发布仓库，在命令末尾加 `--repository <所有者>/<仓库>`。

资源包需符合以下规范：

- 清单使用 `format: 1`。id 最长 64 个字符，以小写字母开头，只含小写字母、数字和连字符；使用新的 id，袖蝶使用保留的 helico-butterfly。版本使用 `1.0.0` 这样的三段数字。
- 名称和描述均提供 zh、en，每个值 1–160 个字符；清单中的 id、版本与目录条目一致。
- ZIP 根目录包含 `manifest.json`、三张基础 WebP，以及成套声明的可选打字图。`rig` 配置位于清单内，预览图放在目录条目中。
- ZIP 本身和解压后的文件总量各不超过 4 MiB；每张 WebP 不超过 2 MiB，清单不超过 64 KiB。图像尺寸、字节数和 SHA-256 必须匹配。
- 预览可使用 PNG 或 WebP，宽高均不超过 512px，编码后的 data URL 不超过 48,000 个字符。

## 4. 在开发版里预览

把 `catalog-v2.json` 复制为同目录的 `catalog.json`。在袖蝶源码开发环境运行下方命令，将示例路径换成 `pet-release/` 的绝对路径。Windows PowerShell 可用 `$env:HELICO_HOME` 和 `$env:HELICO_PET_DIRECTORY` 设置同名变量。

```sh
HELICO_HOME=~/.helico-demo HELICO_PET_DIRECTORY=/path/to/pet-release task run TAGS=purego
```

进入 **设置 → 宠物**，选择新宠物的「下载并使用」。开发版从本地目录读取并校验资源包，测试数据保存在 `~/.helico-demo`。

逐一检查站姿、工作、等待和失败状态，观察眨眼、视线、转身、行走、拖拽与探头是否衔接自然；在最小与最大尺寸、浅色与深色背景、减少动态效果下检查透明边缘和静帧。调整后增加版本、重新构建，再在设置中「更新并使用」。

## 5. 发布资源包

在宠物目录所在的 GitHub 仓库以 `<id>-v<version>` 为标签上传 ZIP，核对下载文件的摘要，再把新条目合并进 `main` 分支的 `catalog-v2.json`。要向袖蝶公开目录提交资源，可附上预览与发行包地址。[袖蝶仓库](https://github.com/run-bigpig/helico) · [提交资源](https://github.com/run-bigpig/helico/issues/new)
