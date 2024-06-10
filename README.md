# ENAMEL

A benchmark for evaluating the capability of large language models (LLMs) in generating efficient code

Comming soon...

[Getting Started](#getting-started) | [Reproduction](#reproduction) | [LLM Leaderboard](#llm-leaderboard) | [Acknowledgements](#acknowledgements)

## About

ENAMEL is a rigorous and high-standard benchmark for evaluating the efficiency of LLM-generated code, which includes:
- TODO

## Getting Started

TODO

## Reproduction

### Using our generated test cases and LLM-generated code

To facilitate reproduction, we share on HuggingFace our [generated test cases](https://huggingface.co/datasets/rq5uiuc/enamel/blob/main/cache/eval~tests.pkl) and [LLM-generated code](https://huggingface.co/datasets/rq5uiuc/enamel/tree/main/samples) used in our evaluation. The code samples should be put in the `samples/` folder. 

To reproduce our results, please run `demo.py`, where `--load_name` specifies the file name of code samples (without file extension), and `--tests` specifies the generated test cases. For example, to evaluate the HumanEval+ canonical solutions, please run:

```bash
python3 demo.py --load_name humanevalplus-canonical --tests cache/eval~tests.pkl
```

### Using zipped code samples provided by EvalPlus

Our demo also supports the zipped code samples provided by [EvalPlus](https://github.com/evalplus/evalplus/releases/tag/v0.1.0). Please put their `.zip` files into our `samples/` folder *without* renaming the files. For example, to evaluate the GPT-4 code samples `gpt-4_temp_0.0.zip` from EvalPlus, please run:

```bash
python3 demo.py --load_name gpt-4_temp_0.0 --tests cache/eval~tests.pkl
```

**Warning:** It is known to us that our evaluator might be unable to kill a code sample if the code uses `try ... except ...` within an infinity loop because the killing signal will be caught. We have decided not to resolve this issue because resolving it with `multiprocessing` will significantly slow down the evaluation process. If you do encounter this issue, please consider removing such code samples. (This issue indeed happens for two code samples provided by EvalPlus, so our demo will automatically handle it if you use the zipped code samples from EvalPlus.) 

## LLM Leaderboard

TODO

## Acknowledgements

TODO
