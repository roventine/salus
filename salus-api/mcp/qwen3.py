from optimum.intel.openvino import OVModelForCausalLM
from transformers import AutoConfig, AutoTokenizer

llm_model_path = r'C:\Users\zangq\Repo\model\OpenVINO\Qwen3-1.7B-int4-ov'

ov_model = OVModelForCausalLM.from_pretrained(
    llm_model_path,
    device='CPU',
)
tokenizer = AutoTokenizer.from_pretrained(llm_model_path)
prompt = "你好."
messages = [{"role": "user", "content": prompt}]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True
)
model_inputs = tokenizer([text], return_tensors="pt")
generated_ids = ov_model.generate(**model_inputs, max_new_tokens=1024)
output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
try:
    index = len(output_ids) - output_ids[::-1].index(151668)
except ValueError:
    index = 0

thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

print("thinking content:", thinking_content)
print("content:", content)