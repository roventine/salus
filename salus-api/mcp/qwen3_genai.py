import openvino_genai as ov_genai
import sys

model_dir = r'C:\Users\zangq\Repo\model\OpenVINO\Qwen3-1.7B-int4-ov'
print(f"Loading model from {model_dir}\n")


pipe = ov_genai.LLMPipeline(str(model_dir), 'CPU')

generation_config = ov_genai.GenerationConfig()
generation_config.max_new_tokens = 32768


def streamer(subword):
    print(subword, end="", flush=True)
    sys.stdout.flush()
    # Return flag corresponds whether generation should be stopped.
    # False means continue generation.
    return False


input_prompt = '''请从今天开始，根据医嘱整理一下未来3个月我需要完成的康复训练。
\begin{tabular}{|c|c|c|c|c|c|}
\hline 术后当天 & 术后 0-1 周 & 术后 1-2 周 & 术后 3-4 周 & 术后 5-6 周 & 术后 7-12 周 \\
\hline 反复冰敷 & 反复冰敷 & 锻炼后冰敷 & 锻炼后冰敷 & 锻炼后冰敷 & 锻炼后冰敷 \\
\hline 踝泵运动 & 踝泵运动 & 踝泵运动 & 踝泵运动 & 踝泵运动 & 踝泵运动 \\
\hline \begin{tabular}{l} 
股四头肌等 \\
长收缩
\end{tabular} & \begin{tabular}{l} 
股四头肌等 \\
长收缩
\end{tabular} & \begin{tabular}{l} 
股四头肌等 \\
长收缩
\end{tabular} & \begin{tabular}{l} 
股四头肌等 \\
长收缩
\end{tabular} & \begin{tabular}{l} 
坐姿多角度 \\
收缩
\end{tabular} & \begin{tabular}{l} 
坐姿多角度 \\
收缩
\end{tabular} \\
\hline & \begin{tabular}{l} 
勾脚直腿抬 \\
高 50 次
\end{tabular} & \begin{tabular}{l} 
勾脚直腿抬 \\
高 100 次
\end{tabular} & \begin{tabular}{l} 
勾脚直腿抬 \\
高 200 次
\end{tabular} & \begin{tabular}{l} 
勾脚直腿抬 \\
高 200 次
\end{tabular} & \begin{tabular}{l} 
勾脚直腿抬 \\
高 200 次
\end{tabular} \\
\hline & 足跟滑动 & 足跟滑动 & 可以不做 & 可以不做 & 可以不做 \\
\hline 伸膝位 & 屈膝 \(<30\) 度 & \begin{tabular}{l} 
2周内屈膝 \(<\) \\
30 度
\end{tabular} & \begin{tabular}{l} 
2-3 周 \(<45\) \\
度 \\
3-4 周 \(<60\) \\
度
\end{tabular} & \begin{tabular}{l} 
4-5 周 \(<75\) \\
度 \\
5-6 周 \(<90\) \\
度
\end{tabular} & \begin{tabular}{l} 
按复查医嘱 \\
调整
\end{tabular} \\
\hline 戴支具 & \begin{tabular}{l} 
拄双拐且患 \\
足不着地 \\
戴支具
\end{tabular} & \begin{tabular}{l} 
拄双拐且患 \\
足不着地 \\
戴支具
\end{tabular} & \begin{tabular}{l} 
拄双拐且患 \\
足不着地 \\
戴支具
\end{tabular} & \begin{tabular}{l} 
拄双拐且患 \\
足不着地 \\
戴支具
\end{tabular} & \begin{tabular}{l} 
拄双拐且患 \\
足不着地 \\
逐步弃支具
\end{tabular} \\
\hline 禁止下蹲 & 禁止下蹲 & 禁止下蹲 & 禁止下蹲 & 禁止下蹲 & \begin{tabular}{l} 
遵医嘱逐步 \\
尝试下蹲 \\
3-4 月内注 \\
意安全
\end{tabular} \\
\hline
\end{tabular}
'''
print(f"Input text: {input_prompt}")
result = pipe.generate(input_prompt, generation_config, streamer)