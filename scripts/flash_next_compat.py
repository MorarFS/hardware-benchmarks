"""Checkpoint-specific norm convention for the pinned Sawfwair MLX conversion.

The converter adds 1 to Qwen4's zero-centered text norm weights. The runtime
must therefore use the stored scale directly. Gated norms and vision norms
already use direct scales and are deliberately untouched. Tensor bytes remain
unchanged; this is a runtime interpretation of the published conversion.
"""
import json
from pathlib import Path

def configure_sawfwair_norms(model_path):
 import mlx.core as mx
 from mlx_vlm.models.qwen4_exp import language
 config=json.loads((Path(model_path)/'config.json').read_text())
 conversion=config.get('mererun_conversion',{})
 assert conversion.get('source_repository')=='Qwen/Qwen3.8-Flash-Next'
 assert conversion.get('source_revision')=='f5d08274bafd880402bd16f5e3e6c514136ec06c'
 assert conversion.get('profile')=='mixed'
 assert conversion.get('converter')=='scripts/model-conversion/convert_qwen38_flash_next_mlx.py'
 def direct_scale_rms_norm(group_size,eps):
  @mx.compile
  def normalize(x,weight):
   dtype=x.dtype;y=x.astype(mx.float32)
   if group_size is not None:
    y=y.reshape(*y.shape[:-1],-1,group_size);weight=weight.reshape(-1,group_size)
   y=y*mx.rsqrt(mx.mean(mx.square(y),axis=-1,keepdims=True)+eps)
   y=y*weight.astype(mx.float32)
   return y.reshape(x.shape).astype(dtype)
  return normalize
 language._qwen4_rms_norm=direct_scale_rms_norm
 return {'name':'Sawfwair direct-scale text RMSNorm compatibility','checkpoint_tensor_values_changed':False,'gated_and_vision_norms_changed':False,'reason':'Publisher converter transform_dense_value stores raw_weight + 1.0 for SHIFTED_TEXT_NORM_SUFFIXES; upstream Qwen4ExpRMSNorm otherwise adds 1.0 a second time.','converter_source':'https://github.com/sawfwair/mere-run/blob/3ed0a15826605c77d9017e33c0a40c9e4e1d1952/scripts/model-conversion/convert_qwen38_flash_next_mlx.py','related_runtime_report':'https://github.com/jundot/omlx/issues/3181'}
