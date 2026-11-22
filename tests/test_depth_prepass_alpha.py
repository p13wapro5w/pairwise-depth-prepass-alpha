import pytest
import render.depth_prepass_alpha as mod

CASES = [
    ("alpha_threshold", (0.5, 0.3)),
    ("double_sided_depth", (1, 2)),
    ("threshold_match", (0.4, 0.5)),
    ("vertex_offset", (1.0, 2.0)),
    ("exclude_transparent", (1, 2)),
    ("earlyz_split", (1, 2)),
    ("depth_precision", (16, 24)),
    ("write_pair", (1, 2)),
    ("multi_pass_merge", (2, 3)),
    ("shadow_prepass", (1, 2)),
    ("stencil_mask", (1, 2)),
    ("depth_test", (1.0, 0.5)),
    ("clip_plane", (0.1, 100.0)),
    ("bias_apply", (0.001, 0.002)),
    ("prepass_order", (1, 2)),
]

@pytest.mark.parametrize("fn_name,args", CASES)
def test_contract(fn_name, args):
    fn = getattr(mod, fn_name)
    assert fn(*args) is not None
