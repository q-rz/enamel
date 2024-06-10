from enam import *

def get_args(*args, **kwargs): # arguments for the demo
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_name', type = str, help = 'file name of the code samples to evaluate (without file extension)')
    parser.add_argument('--save_name', type = str, default = 'cache/eval', help = 'prefix for saving results')
    parser.add_argument('--seed', type = int, default = 998244353, help = 'random seed')
    parser.add_argument('--n_tests', type = parse_int_list, default = [8, 4, 4, 4], help = 'numbers of tests to generate for each level (default: 8,4,4,4)')
    parser.add_argument('--n_reps', type = int, default = 6, help = 'number of repeats per test case')
    parser.add_argument('--hardness', type = parse_float_list, default = [0., 3., 3., 4.], help = 'hardnesses of each level (default: 0,3,3,4)')
    parser.add_argument('--memory_giga', type = float, default = 4., help = 'memory limit (in gigabytes)')
    parser.add_argument('--timeout_factor', type = float, default = 2., help = 'timeout factor alpha')
    parser.add_argument('--tolerence_sec', type = float, default = 0.01, help = 'time limit tolerence (in seconds)')
    parser.add_argument('--eval_k', type = parse_int_list, default = [1, 10, 100], help = '(default: 1,10,100)')
    parser.add_argument('--verbose', type = parse_bool, default = False, choices = [True, False], help = 'whether to print results for each test case (True/False)')
    parser.add_argument('--dataset', type = str, default = 'dataset/enamel.csv', help = 'file name of the ENAMEL dataset')
    parser.add_argument('--subset', type = parse_int_list, default = PROBLEMSET, help = 'problems to be evaluated (comma separated; no whitespaces)')
    parser.add_argument('--tests', type = str, default = None, help = 'file name of the generated tests')
    parser.add_argument('--json_path', type = str, default = 'samples/', help = 'folder for JSON code samples')
    parser.add_argument('--zip_path', type = str, default = 'samples/', help = 'folder for zipped code samples')
    parser.add_argument('--tmp_path', type = str, default = 'cache/', help = 'temporary path to save unzipped code samples')
    return Dict(vars(parser.parse_args(*args, **kwargs)))

def load_evalplus_zip(zip_fname: str, tmp_path: str): # loads the zipped code samples from EvalPlus
    os.makedirs(tmp_path, exist_ok = True)
    os.system(f'unzip -o -qq {zip_fname} -d {tmp_path}') # 
    while True:
        files = os.listdir(tmp_path)
        if len(files) != 1:
            break
        tmp_path = osp.join(tmp_path, files[0])
    print('Unzipped to', tmp_path, flush = True)
    n_problems = max(int(problem_id.split('_')[-1]) for problem_id in os.listdir(tmp_path) if problem_id.startswith('HumanEval_')) + 1
    codes = [[] for i in range(n_problems)]
    for i in range(n_problems):
        code_path = osp.join(tmp_path, f'HumanEval_{i}')
        for code_fname in os.listdir(code_path):
            if code_fname.endswith('.py'):
                j = int(code_fname[: -3])
                if j >= len(codes[i]):
                    codes[i].extend([None] * (j - len(codes[i]) + 1))
                with open(osp.join(code_path, code_fname)) as fi:
                    code = fi.read()
                if code.startswith('python\n'): # the code was parsed incorrectly
                    code = code[7 :]
                # remove examples in the code
                for key in ['\n# Examples\n', '\n# Example usage:\n', '\n# Test cases\n']:
                    pos = code.find(key)
                    if pos != -1:
                        code = code[: pos]
                codes[i][j] = code
    # dead loops that cannot be killed are replaced with a loop that can be killed
    LOOP_CODE = 'while True:\n    pass\n'
    if zip_fname.endswith('/gptneo-2b_temp_0.8.zip'):
        if ' try:' in codes[107][88]:
            codes[107][88] = LOOP_CODE
    elif zip_fname.endswith('/codegen2-1b_temp_0.8.zip'):
        if ' try:' in codes[77][123]:
            codes[77][123] = LOOP_CODE
    return codes

class Loader: # loader of code samples (JSON files are recommended; zip files from EvalPlus are also supported)
    def __init__(self, json_path, zip_path = None, tmp_path = None):
        self.json_path = json_path
        self.zip_path = zip_path
        self.tmp_path = tmp_path
    def load(self, name): # returns either dict or list
        json_fname = osp.join(self.json_path, name + '.json')
        if osp.isfile(json_fname):
            print('Loading', json_fname)
            with open(json_fname) as fi:
                codes = json.load(fi)
            if isinstance(codes, dict):
                return {int(i): codes_i for i, codes_i in codes.items()}
            else:
                return codes
        else:
            zip_fname = osp.join(self.zip_path, name + '.zip')
            if osp.isfile(zip_fname):
                print('Loading', json_fname)
                return load_evalplus_zip(zip_fname, osp.join(self.tmp_path, name))
            else:
                raise ValueError(f'unrecognized name {name}')

def main(args: Dict):
    evaluator = Evaluator(
        problems = args.dataset, subset = args.subset,
        n_tests = args.n_tests, n_reps = args.n_reps,
        hardness = args.hardness,
        memory_giga = args.memory_giga,
        timeout_factor = args.timeout_factor, tolerence_sec = args.tolerence_sec,
        seed = args.seed,
    )
    if args.tests is None or not evaluator.load_tests(fname = args.tests):
        if args.tests is not None: print('[Notice] tests not found', flush = True)
        evaluator.make_tests(save_name = args.save_name)

    loader = Loader(json_path = args.json_path, zip_path = args.zip_path, tmp_path = args.tmp_path)
    load_name = args.load_name
    print('>>>', load_name, flush = True)
    codes = loader.load(load_name)
    metrics = evaluator.evaluate(codes, k = args.eval_k, save_name = f'{args.save_name}~{load_name}', verbose = args.verbose)
    print(metrics)

if __name__ == '__main__':
    main(get_args())
