# ENAMEL

[![Our paper on arXiv](https://github.com/q-rz/enamel/raw/main/figures/img.shields.io%20badge%202406.06647-arXiv-B31B1B.svg)](https://arxiv.org/abs/2406.06647) [![Our dataset on HuggingFace](https://github.com/q-rz/enamel/raw/main/figures/img.shields.io%20badge%20enamel-HuggingFace-FF9D0B.svg)](https://doi.org/10.57967/hf/2456) [![Our Python library on PyPI](https://github.com/q-rz/enamel/raw/main/figures/img.shields.io%20badge%20enam-PyPI-006DAD.svg)](https://pypi.org/project/enam/)

[Getting Started](#getting-started) | [Library Usage](#library-usage) | [LLM Leaderboard](#llm-leaderboard) | [Acknowledgements](#acknowledgements)

## What is ENAMEL?

ENAMEL is a rigorous and high-standard benchmark for evaluating the capability of large language models (LLMs) in generating efficient code. We provide:

- A new metric $\text{eff}@k$ characterizing the relationship between code efficiency and sample size $k$;
- A problem set consisting of 142 high-quality problems selected from [OpenAI HumanEval](https://github.com/openai/human-eval);
- Expert-written efficient reference solutions, setting a high-standard for efficiency evaluation;
- Expert-written strong test case generators, enabling a rigorous evaluation of both correctness and efficiency;
- A Python library `enam` for easily evaluating the efficiency of LLM-generated code.

If you are interested in our work, please feel free to check [our paper](https://arxiv.org/abs/2406.06647) for detail.

<center><img src="https://github.com/q-rz/enamel/raw/main/figures/fig-enamel.svg" alt="Illustration of ENAMEL" style="max-width:1000px;width:100%;" /></center>

## Getting Started

### Dependencies

Before running the code, please ensure the following dependencies:

- Python >= 3.10
- Tqdm >= 3.1.4
- NumPy >= 1.4.0
- Pandas >= 1.0

### Using our generated test cases and LLM-generated code samples

To facilitate reproduction, we share on HuggingFace our [generated test cases](https://huggingface.co/datasets/q-rz/enamel/blob/main/cache/eval~tests.pkl) and [LLM-generated code samples](https://huggingface.co/datasets/q-rz/enamel/tree/main/samples) used in our evaluation. Please download `eval~tests.pkl` into the `cache/` folder and download the code samples into the `samples/` folder. 

To reproduce our results, please run `demo.py`, where `--load_name` specifies the file name of code samples (without file extension), and `--tests` specifies the generated test cases. For example, to evaluate the HumanEval+ canonical solutions, please run:
```sh
python3 demo.py --load_name humanevalplus-canonical --tests cache/eval~tests.pkl
```

### Evaluating zipped code samples provided by EvalPlus

Our demo also supports the zipped code samples provided by [EvalPlus](https://github.com/evalplus/evalplus/releases/tag/v0.1.0). Please put their `.zip` files into our `samples/` folder *without* renaming the files. For example, to evaluate the GPT-4 code samples `gpt-4_temp_0.0.zip` from EvalPlus, please run:
```sh
python3 demo.py --load_name gpt-4_temp_0.0 --tests cache/eval~tests.pkl
```

**Warning:** It is known to us that our evaluator might be unable to kill a code sample if the code uses `try ... except ...` within an infinity loop because the killing signal will be caught. We have decided not to resolve this issue because resolving it with `multiprocessing` will significantly slow down the evaluation process. If you do encounter this issue, please consider removing such code samples. (This issue indeed happens for two code samples provided by EvalPlus, so our demo will automatically handle it if you use the zipped code samples from EvalPlus.) 

### Evaluating new code samples

If you want to evaluate your own code samples, please organize them as a `.json` file, put it in the `samples/` folder, and run `demo.py`. For example, if the code samples are in the file `samples/codes.json`, please run:
```sh
python3 demo.py --load_name codes --tests cache/eval~tests.pkl
```
The `.json` file should be a dict of lists such that `codes[str(i)][j]` is the $j$-th code sample of problem $i$.

## Library Usage

Our benchmark is also available as a Python library. Please see `demo.py` for an example usage of our library. 

**Notice:** DO NOT use multiple threads or processes in efficiency evaluation. That might negatively affect the efficiency results.

### Installation

Our library `enam` can be installed via `pip`:
```sh
pip install enam --upgrade
```

**Note:** To distinguish from our benchmark ENAMEL, we name our library `enam`.

## LLM Leaderboard

The following table is a leaderboard of 30 LLMs (under greedy decoding) as well as HumanEval/HumanEval+ canonical solutions. Results show that LLMs fall short of generating expert-level efficient code. For more results, please refer to our paper.

We welcome LLM developers to submit their results to enrich this leaderboard. If you would like to submit your results, please organize your generated code samples into a `.json` file as described above and contact Ruizhong Qiu (rq5 AT illinois DOT edu).

|No.|Name|eff@1|pass@1|
|:-:|:-|:-:|:-:|
|1|HumanEval+|0.517|0.958|
|2|GPT-4 Turbo (Nov 2023)|0.470|0.796|
|3|HumanEval|0.458|0.908|
|4|GPT-4 (Jun 2023)|0.454|0.831|
|5|Llama 3 70B Instruct|0.421|0.746|
|6|Mixtral 8x22B Instruct|0.408|0.746|
|7|Claude 3 Opus|0.401|0.789|
|8|Phind Code Llama V2|0.394|0.683|
|9|Claude 3 Haiku|0.386|0.739|
|10|ChatGPT|0.364|0.683|
|11|Claude 3 Sonnet|0.345|0.662|
|12|Llama 3 8B Instruct|0.344|0.592|
|13|Code Llama 34B Python|0.268|0.458|
|14|Mixtral 8x7B Instruct|0.266|0.444|
|15|Code Llama 70B Python|0.264|0.500|
|16|Code Llama 7B Python|0.247|0.373|
|17|Code Llama 13B Python|0.216|0.408|
|18|StarCoder|0.195|0.352|
|19|CodeGen 6B|0.193|0.296|
|20|CodeGen 16B|0.169|0.310|
|21|CodeT5+ 16B|0.160|0.317|
|22|CodeGen 2B|0.153|0.254|
|23|Mistral 7B|0.152|0.275|
|24|Vicuna 13B|0.123|0.176|
|25|SantaCoder|0.100|0.141|
|26|Incoder 6B|0.091|0.127|
|27|GPT-J|0.083|0.106|
|28|Incoder 1B|0.066|0.092|
|29|Vicuna 7B|0.061|0.099|
|30|GPT-Neo 2B|0.043|0.056|
|31|PolyCoder|0.037|0.049|
|32|StableLM 7B|0.020|0.021|

## Acknowledgements

- [OpenAI HumanEval](https://github.com/openai/human-eval)
- [EvalPlus](https://github.com/evalplus/evalplus)
- [HuggingFace CodeEval](https://huggingface.co/spaces/evaluate-metric/code_eval)
