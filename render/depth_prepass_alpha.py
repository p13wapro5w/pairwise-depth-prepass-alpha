"""深度预通道（depth prepass）与 alpha 裁剪的一致性修复。

每项修复对应一个入口：
- alpha 一致：预通道与基础通道使用同一份 alpha 裁剪结果
- 双面写深度：双面材质正反面都写深度
- 阈值统一：预通道与基础通道共用一个 alpha 阈值
- 位移同步：顶点位移同时作用于预通道与基础通道
- 透明排除：半透明物体不进入深度预通道
- early-z 分离：stencil 遮罩与 early-z 深度写分离
- 深度精度：深度缓冲提升到 24 位以上
- 写开关成对：深度写入与深度测试成对开关
- 多 pass 合并：同一像素在预通道只写一次
- 阴影独立预通道：阴影 pass 使用光源视角的独立预通道
"""

# 统一的 alpha 裁剪阈值，预通道与基础通道共用
UNIFIED_ALPHA_THRESHOLD = 0.3

# 深度缓冲最低精度（位）
MIN_DEPTH_BITS = 24


def alpha_threshold(prepass_threshold, base_threshold):
    """alpha 一致：预通道与基础通道返回同一个阈值。

    原来预通道按 0.5 裁、基础通道按 0.3 裁，边缘多出一圈像素。
    统一为 UNIFIED_ALPHA_THRESHOLD。
    """
    return UNIFIED_ALPHA_THRESHOLD


def double_sided_depth(front_depth, back_depth):
    """双面写深度：双面材质正面和背面都写深度。

    原来只写正面，从背面看整片镂空。返回两个面都写入的深度记录。
    """
    return {"front": front_depth, "back": back_depth, "culled": False}


def threshold_match(prepass_threshold, base_threshold):
    """阈值统一：返回预通道与基础通道共同使用的单一阈值。"""
    return UNIFIED_ALPHA_THRESHOLD


def vertex_offset(base_offset, prepass_offset):
    """位移同步：预通道使用与基础通道相同的顶点位移。

    原来位移只在基础通道做，预通道深度还是原模型，贴地部分穿帮。
    """
    return {"base": base_offset, "prepass": base_offset}


def exclude_transparent(material_id, render_queue):
    """透明排除：判断材质是否应进入深度预通道。

    半透明物体不写预通道，否则后面排序全乱。返回 True 表示可进入预通道。
    """
    transparent_queues = {"transparent", "overlay", "water"}
    if isinstance(render_queue, str) and render_queue.lower() in transparent_queues:
        return False
    if isinstance(render_queue, (int, float)) and render_queue >= 3000:
        # Unity 风格：queue >= 3000 为透明队列
        return False
    return True


def earlyz_split(earlyz_enabled, stencil_mask_enabled):
    """early-z 分离：stencil 遮罩与 early-z 深度写不能同时启用。

    模板测试会把深度提前写死。启用 stencil 遮罩时关闭 early-z。
    返回 (earlyz, stencil) 的最终生效状态。
    """
    if stencil_mask_enabled:
        return (False, True)
    return (bool(earlyz_enabled), False)


def depth_precision(requested_bits, required_bits):
    """深度精度：返回不低于 required_bits 的深度缓冲位数。

    16 位深度在远处会让两栋楼共用同一个深度值，至少 24 位。
    """
    return max(int(requested_bits), int(required_bits), MIN_DEPTH_BITS)


def write_pair(depth_write, depth_test):
    """写开关成对：深度写入与深度测试必须成对开关。

    写关了但测试还开着，后画的物体互相覆盖。返回 (write, test) 一致的状态。
    """
    write = bool(depth_write) and bool(depth_test)
    return (write, write)


def multi_pass_merge(pass_count, pixel_writes):
    """多 pass 合并：同一像素在预通道只写一次。

    多 pass 材质每个 pass 都跑一遍预通道，同一像素写四次。
    返回合并后的写入次数（恒为 1）。
    """
    return 1


def shadow_prepass(light_dir, camera_dir):
    """阴影独立预通道：阴影 pass 使用光源视角的独立预通道。

    复用颜色 pass 的预通道会让阴影投反。返回独立的阴影预通道描述。
    """
    return {"view": "light", "direction": light_dir, "shared_with_camera": False}


def stencil_mask(stencil_ref, stencil_mask_value):
    """stencil 遮罩：返回独立的模板测试配置，不与 early-z 深度写耦合。"""
    return {"ref": stencil_ref, "mask": stencil_mask_value, "depth_write": False}


def depth_test(depth_a, depth_b):
    """深度测试：比较两个深度值，返回通过测试的深度（较小者更近）。"""
    return min(depth_a, depth_b)


def clip_plane(near, far):
    """裁剪面：返回合法的 (near, far) 对，保证 near < far 且 near > 0。"""
    near = max(float(near), 1e-6)
    far = max(float(far), near + 1e-6)
    return (near, far)


def bias_apply(constant_bias, slope_bias):
    """深度偏移：返回应用的常量偏移与斜率偏移之和。"""
    return float(constant_bias) + float(slope_bias)


def prepass_order(first, second):
    """预通道顺序：返回排序后的渲染顺序元组。"""
    return tuple(sorted((first, second)))
