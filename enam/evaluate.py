from .header import *
from .execute import *
from . import datautils

datautils = vars(datautils)

def calc_exec_time(ts): # Hodges--Lehmann estimator
    ts = np.array(ts) / 2.
    ts = ts[None, :] + ts[:, None]
    ts = ts[np.tril_indices_from(ts)]
    return np.median(ts)

def calc_eff(elapsed, ref, timeout):
    return max(0., timeout - elapsed) / (timeout - ref)

def calc_eff_at_k(e, k): # numerically stable implementation
    n = len(e)
    lbd = [k / n]
    k_ = k - 1
    for r in range(n - 1, k_, -1):
        lbd.append(lbd[-1] * (1 - k_ / r))
    lbd = np.flip(lbd)
    e = np.sort(e)[k_ :]
    return (lbd * e).sum()

def calc_pass_at_k(n, c, k): # from the HumanEval paper
    if n - c < k: return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

class Test: # a test case
    def __init__(self, input = None, answer = None, ref = None):
        self.input = input
        self.answer = answer
        self.ref = ref # reference execution time

class Refs: # references for efficiency evaluation
    def __init__(self, tests, hardness):
        neg_inf = float('-inf')
        self.refs = [neg_inf] * len(hardness)
        self.ref_max = neg_inf
        self.lid = None
        self.cid = None
        # finds the longest reference execution time for calibration
        for j, (size, tests_j) in enumerate(tests):
            if hardness[j]:
                for k, test in enumerate(tests_j):
                    if self.refs[j] < test.ref:
                        self.refs[j] = test.ref
                        if self.ref_max < test.ref:
                            self.ref_max = test.ref
                            self.lid = j
                            self.cid = k

class Evaluator:
    TPL_MAKE = '''%s
%s
random.seed(%d)
__input = generate_input(size = %d, lid = %d, cid = %d)
''' # (prompt, generator, seed, size)
    TPL_RUN = '''%s
%s
__t0 = time.time()
__output = %s(*__input)
__t1 = time.time()
''' # (prompt, solution, entry_point)
    TPL_TEST = '''%s
    pass
%s
__accepted = __check(__input, __answer, __output)
''' # (prompt, checker)
    def __init__(self, problems, subset, n_tests: int, n_reps: int, hardness, memory_giga: float, timeout_factor: float, tolerence_sec: float, seed: int):
        self.problems = pd.read_csv(problems)
        self.n_problems = self.problems.shape[0]
        self.subset = list(range(self.n_problems)) if subset is None else sorted(set(subset))
        self.n_tests = n_tests
        self.hardness = np.array(hardness)
        self.n_levels = len(self.hardness)
        self.n_reps = [n_reps if self.hardness[j] else 1 for j in range(self.n_levels)] # no need to repeat if it does not count into the efficiency score
        self.memory = memory_giga * (1024 ** 3)
        self.timeout_factor = timeout_factor
        self.tolerence_sec = tolerence_sec
        self.tests = [[] for i in range(self.n_problems)]
        self.refs = [None for i in range(self.n_problems)]
        self.seed = seed
    def make_tests(self, save_name = None):
        tbar = tqdm(self.subset)
        for i in tbar:
            tbar.set_description(f'Generating inputs for #{i}')
            problem = self.problems.iloc[i]
            seed = 0
            for j, size in enumerate(list(map(int, problem.input_levels.split()))):
                tests = []
                for k in range(self.n_tests[j]):
                    scope = dict(time = time, **datautils)
                    unsafe_execute(self.TPL_MAKE % (problem.prompt, problem.input_generator, self.seed ^ i ^ (seed + k), size, j, k), scope) # assuming that the input generator is error-free
                    tests.append(Test(input = scope['__input']))
                self.tests[i].append((size, tests))
                seed += self.n_tests[j]
        tbar = tqdm(self.subset)
        for i in tbar:
            tbar.set_description(f'Computing answers for #{i}')
            problem = self.problems.iloc[i]
            for j, (size, tests) in enumerate(self.tests[i]):
                n_reps = self.n_reps[j]
                for test in tests:
                    refs = [None for rep in range(n_reps)]
                    for rep in range(n_reps):
                        scope = dict(time = time, __input = deepcopy(test.input))
                        unsafe_execute(self.TPL_RUN % (problem.prompt, problem.reference_solution, problem.entry_point), scope) # assuming that the reference solution is error-free
                        refs[rep] = scope['__t1'] - scope['__t0']
                    test.answer = scope['__output']
                    test.ref = calc_exec_time(refs).item()
            self.refs[i] = Refs(self.tests[i], self.hardness)
        if save_name is not None:
            fname = f'{save_name}~tests.pkl'
            with open(fname, 'wb') as fo:
                pickle.dump((self.tests, self.refs), fo)
            print('Tests saved to', fname, flush = True)
    def load_tests(self, fname):
        if osp.isfile(fname):
            with open(fname, 'rb') as fi:
                self.tests, self.refs = pickle.load(fi)
            print('Tests loaded from', fname, flush = True)
            return True
        else:
            return False
    def get_time_correction(self, i): # computes the calibration factor of of execution time
        j = self.refs[i].lid
        k = self.refs[i].cid
        problem = self.problems.iloc[i]
        test = self.tests[i][j][-1][k]
        n_reps = self.n_reps[j]
        elapsed = [None for rep in range(n_reps)]
        for rep in range(n_reps):
            scope = dict(time = time, __input = deepcopy(test.input)) # in case that the code modifies the input
            unsafe_execute(self.TPL_RUN % (problem.prompt, problem.reference_solution, problem.entry_point), scope) # assuming that the reference solution is error-free
            elapsed[rep] = scope['__t1'] - scope['__t0']
        elapsed = calc_exec_time(elapsed).item()
        return self.refs[i].ref_max / elapsed
    def zero_effs(self):
        return [0. for j in range(self.n_levels)]
    def evaluate1(self, i, code, time_correction, verbose): # evaluates one code sample
        problem = self.problems.iloc[i]
        refs = self.refs[i]
        timeout = self.timeout_factor * refs.ref_max / time_correction
        effs = []
        elapsed_list = []
        for j, (size, tests) in enumerate(self.tests[i]):
            n_reps = self.n_reps[j]
            level_elapsed = []
            level_break = False
            for k, test in enumerate(tests):
                elapsed = [None for rep in range(n_reps)]
                for rep in range(n_reps):
                    scope = dict(time = time, input = None, print = None, __input = deepcopy(test.input)) # in case that the code modifies the input
                    try:
                        unsafe_timed_execute(self.TPL_RUN % (problem.prompt, code, problem.entry_point), scope, self.memory, timeout + self.tolerence_sec)
                        scope['__input'] = test.input
                        scope['__answer'] = test.answer # to prevent the code reading the answer
                        unsafe_execute(self.TPL_TEST % (problem.prompt, problem.checker), scope) # assuming that the checker does not modify the input
                    except TimeoutException as e:
                        if verbose: print(f'[problem={i}, level={j}, case={k}] Time Limit Exceeded (size={size}, timeout={timeout:.4f})')####
                        level_break = True
                        break
                    except MemoryError as e:
                        if verbose: print(f'[problem={i}, level={j}, case={k}] Out of Memory (size={size})')####
                        level_break = True
                        break
                    except OverflowError as e:
                        if verbose: print(f'[problem={i}, level={j}, case={k}] Overflow Error (size={size})')####
                        level_break = True
                        break
                    except KeyboardInterrupt as e:
                        raise e
                    except BaseException as e:
                        if verbose: print(f'[problem={i}, level={j}, case={k}] {type(e)}: {e}')####
                        return False, self.zero_effs(), elapsed_list
                    else:
                        if '__accepted' in scope and scope['__accepted']:
                            elapsed[rep] = scope['__t1'] - scope['__t0']
                        else:
                            if verbose: print(f'[problem={i}, level={j}, case={k}] Wrong output')####
                            return False, self.zero_effs(), elapsed_list
                if level_break:
                    break
                else:
                    level_elapsed.append(calc_exec_time(elapsed).item() * time_correction)
            elapsed_list.append(level_elapsed)
            if level_break:
                break
            else:
                effs.append(calc_eff(elapsed = max(level_elapsed), ref = refs.refs[j], timeout = timeout))
        if j == 0 and level_break:
            return False, self.zero_effs(), elapsed_list
        for j in range(len(effs), self.n_levels):
            effs.append(0.)
        return True, effs, elapsed_list
    def evaluate(self, codes, k, save_name = None, verbose = False): # evaluates all code samples
        if isinstance(k, int):
            k = [k]
        min_codes = min(len(codes[i]) for i in self.subset)
        k = sorted({k_ for k_ in k if k_ <= min_codes})
        passes = [0. for k_ in k]
        effs = [0. for k_ in k]
        passes_ = dict()
        effs_ = dict()
        elapsed_ = dict()
        tbar = tqdm(self.subset, desc = 'Evaluating')
        gc.collect()
        for i in tbar:
            tbar.set_description(f'Evaluating #{i}')
            time_correction = self.get_time_correction(i = i)
            n_levels = len(self.tests[i])
            problem_passes = []
            problem_effs = []
            problem_elapsed = []
            for code in codes[i]:
                passed, code_effs, code_elapsed = self.evaluate1(i = i, code = code, time_correction = time_correction, verbose = verbose)
                problem_passes.append(passed)
                problem_effs.append(code_effs)
                problem_elapsed.append(code_elapsed)
            passes_[i] = deepcopy(problem_passes)
            effs_[i] = deepcopy(problem_effs)
            elapsed_[i] = problem_elapsed
            for j, k_ in enumerate(k):
                passes[j] += calc_pass_at_k(n = len(problem_passes), c = sum(problem_passes), k = k_)
                effs[j] += calc_eff_at_k(e = np.average(problem_effs, axis = 1, weights = self.hardness), k = k_)
        metrics = dict()
        n_problems = len(self.subset)
        for k_, pass_k in zip(k, passes):
            metrics[f'pass@{k_}'] = pass_k / n_problems
        for k_, eff_k in zip(k, effs):
            metrics[f'eff@{k_}'] = eff_k / n_problems
        if save_name is not None:
            with open(f'{save_name}~passes.json', 'w') as fo:
                json.dump(passes_, fo)
            with open(f'{save_name}~effs.json', 'w') as fo:
                json.dump(effs_, fo)
            with open(f'{save_name}~elapsed.json', 'w') as fo:
                json.dump(elapsed_, fo)
            with open(f'{save_name}~metrics.json', 'w') as fo:
                json.dump(metrics, fo)
        return metrics
