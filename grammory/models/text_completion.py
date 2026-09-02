from pydantic import BaseModel
from typing import List, Dict, Optional

class ResultItem(BaseModel):
    text: str

class TextCompletionResponse(BaseModel):
    results: List[ResultItem]

class TextCompletionRequest(BaseModel):
    n: int = 1
    max_context_length: int = 8192
    max_length: int = 2000
    rep_pen: float = 1.02
    temperature: float = 0.3
    top_p: float = 0.6
    top_k: int = 25
    top_a: float = 0
    typical: float = 1
    tfs: float = 1
    rep_pen_range: int = 360
    rep_pen_slope: float = 0.7
    sampler_order: List[int] = [6, 0, 1, 3, 4, 2, 5]
    memory: str = ""
    trim_stop: bool = True
    genkey: str = ""
    min_p: float = 0
    dynatemp_range: float = 0
    dynatemp_exponent: float = 1
    smoothing_factor: float = 0
    smoothing_curve: float = 1
    nsigma: float = 0
    banned_tokens: List[str] = []
    render_special: bool = False
    logprobs: bool = False
    reasoning_effort: str = "none"
    replace_instruct_placeholders: bool = True
    presence_penalty: float = 0
    logit_bias: Dict[str, float] = {}
    adaptive_target: float = -1
    adaptive_decay: float = 0.9
    stop_sequence: List[str] = ["{{[INPUT]}}", "{{[OUTPUT]}}"]
    use_default_badwordsids: bool = False
    bypass_eos: bool = False
    prompt: str
    grammar: str