# ENAMEL

Under construction. Comming soon...

[Getting Started](#getting-started) | [Library Usage](#library-usage) | [LLM Leaderboard](#llm-leaderboard) | [Acknowledgements](#acknowledgements)

## What is ENAMEL?

ENAMEL is a rigorous and high-standard benchmark for evaluating the capability of large language models (LLMs) in generating efficient code. We provide:
- A new metric $\text{eff}@k$ characterizing the relationship between code efficiency and sample size $k$;
- A problem set consisting of 142 high-quality problems selected from [OpenAI HumanEval](https://github.com/openai/human-eval);
- Expert-written efficient reference solutions, setting a high-standard for efficiency evaluation;
- Expert-written strong test case generators, enabling a rigorous evaluation of both correctness and efficiency;
- A Python library for easily evaluating the efficiency of LLM-generated code.

## Getting Started

### Dependencies

Before running the code, please ensure the following dependencies:
- Python >= 3.10
- Tqdm >= 3.1.4
- NumPy >= 1.4.0
- Pandas >= 1.0

### Using our generated test cases and LLM-generated code samples

To facilitate reproduction, we share on HuggingFace our [generated test cases](https://huggingface.co/datasets/rq5uiuc/enamel/blob/main/cache/eval~tests.pkl) and [LLM-generated code samples](https://huggingface.co/datasets/rq5uiuc/enamel/tree/main/samples) used in our evaluation. Please download `eval~tests.pkl` into the `cache/' folder and download the code samples into the `samples/` folder. 

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

TODO

## LLM Leaderboard

The following table is a leaderboard of 30 LLMs under greedy decoding. For more results, please refer to our paper.

We welcome LLM developers to submit their results to enrich this leaderboard. If you want to submit your results, please organize the generated code samples into a `.json` file and contact Ruizhong Qiu (rq5 AT illinois DOT edu).

TODO

## Acknowledgements

- [OpenAI HumanEval](https://github.com/openai/human-eval)
- [EvalPlus](https://github.com/evalplus/evalplus)
- [HuggingFace CodeEval](https://huggingface.co/spaces/evaluate-metric/code_eval)
