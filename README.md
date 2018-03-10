![law](https://raw.githubusercontent.com/riga/law/master/logo.png)

# SingleTop Analysis with Public CMS Data using *law*

**Note**: This example is still under development. Apologies for missing documentation at some places.


This example analysis uses CMS Open Data (2011) to perform a very simple singletop analysis. It is desined to showcase the [**luigi analysis workflow**](https://github.com/riga/law) (law) package.


### Getting started

To get familiar with law, have a look at these simple examples:

- [loremipsum](https://github.com/riga/law/tree/master/examples/loremipsum) (measuring character frequencies)
- [lsf_at_cern](https://github.com/riga/law/tree/master/examples/lsf_at_cern) (workflows that submit tasks via LSF)


### Requirements

The tasks in this example analysis require docker to be installed on your system. Other dependencies can be conveniently installed via

```bash
$ ./devinstall.sh
```

This will create a directory `devsoftware` at the top level directory with all required python packages ([luigi](https://github.com/spotify/luigi), [six](https://github.com/benjaminp/six), [scinum](https://github.com/riga/scinum), [law](https://github.com/riga/law), and [order](https://github.com/riga/order)).


### Setup

Source the `devsoftware`:

```bash
$ source devenv.sh
```

Setup a few environment variables used by the singletop analysis:

```bash
$ source singletop.sh
```

If you want to see the tasks' dependency tree and progress live in your browser, open a second shell, source the `devenv.sh` script and start a central luigi scheduler:

```bash
$ luigid
```

If you decided to use the central scheduler, you can omit the `--local-scheduler` parameters in all commands below.

Now you're good to go.


### Running the Analysis

The analysis configuration is placed in [analysis/framework](https://github.com/riga/law_example_CMSSingleTopAnalysis/blob/master/analysis/framework) (too big a word for what it actually contains). It contains a stack plotting method, and the implementation of selection, reconstruction and systematics. Those are not designed to be very performant - their purpose is to show event-by-event processing within law tasks. Although backed by numpy arrays, the processing is not numpy-vectorized for the sake of using TLorentzVector's.

The [analysis/setup](https://github.com/riga/law_example_CMSSingleTopAnalysis/blob/master/analysis/setup) directory contains the definition of input datasets, physics processes and constants, cross sections, and generic analysis information using the order package. Especially processes and datasets could be candidates for public provisioning of LHC experiment data.

The actual analysis is defined in [analysis/tasks/simple.py](https://github.com/riga/law_example_CMSSingleTopAnalysis/blob/master/analysis/tasks/simple.py). The tasks in this file rely on some base classes (`AnalysisTask`, `ConfigTask`, `ShiftTask`, and `DatasetTask`, see [analysis/framework/tasks.py](https://github.com/riga/law_example_CMSSingleTopAnalysis/blob/master/analysis/framework/tasks.py)), which are defined along the major objects provided by order.

Let law scan your the tasks and their parameters:

```bash
$ law db

loading tasks from 1 module(s)
written 5 task(s) to db file '/law_example_CMSSingleTopAnalysis/.law/db'
```

The created file is only used for faster auto-completion of your tasks (e.g. try `law run <tab><tab>`), and for finding the correct model to load based on the *task family* you want to run. In general, law could also work without the *db* file, but it's very convenient.

Now, fetch the CMS Open Data file containing singletop events:

```bash
$ law run singletop.FetchData --version v1 --dataset singleTop --local-scheduler
```

Check that the task output exists:

```bash
$ law run singletop.FetchData --version v1 --dataset singleTop --print-status 0

print task status with max_depth 0 and target_depth 0

> check status of singletop.FetchData(version=v1, effective_shift=nominal, dataset=singleTop)
|   - check LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop/FetchData/singletop_opendata_2011/singleTop/nominal/v1/data.root)
|     -> existent
```

The file exists. The path of the `LocalFileTarget` is quite long, which is not particularly law-specific but rather subject to the base task classes in this example. However, in reality, one shouldn't care too much about the exact paths, as long as task parameters are encoded consistently.

Try to delete the output again:

```bash
$ law run singletop.FetchData --version v1 --dataset singleTop --remove-output 0

remove task output with max_depth 0
removal mode? [i*(interactive), a(all), d(dry)] # type 'a'

selected all mode

> remove output of singletop.FetchData(version=v1, effective_shift=nominal, dataset=singleTop)
|   - remove LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop/FetchData/singletop_opendata_2011/singleTop/nominal/v1/data.root)
|     removed
```

(`--remove-output 0,a` would have get you to the same result without the prompt)

The number passed to both `--print-status` and `--remove-output` is the tree depth. 0 means the only the task itself, 1 means the first level of dependencies, etc, and negative numbers mean full recursion (handle with care).

Now, you can run the selection and reconstruction. First, check the status of the task to get an idea of that the command will execute:

```bash
$ law run singletop.SelectAndReconstruct --version v1 --dataset singleTop --print-status -1

print task status with max_depth -1 and target_depth 0

> check status of singletop.SelectAndReconstruct(version=v1, effective_shift=nominal, dataset=singleTop)
|   - check LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop/SelectAndReconstruct/singletop_opendata_2011/singleTop/nominal/v1/data.npz)
|     -> absent
|
|   > check status of singletop.ConvertData(version=v1, effective_shift=nominal, dataset=singleTop)
|   |   - check LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop/ConvertData/singletop_opendata_2011/singleTop/nominal/v1/data.npz)
|   |     -> absent
|   |
|   |   > check status of singletop.FetchData(version=v1, effective_shift=nominal, dataset=singleTop)
|   |   |   - check LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop/FetchData/singletop_opendata_2011/singleTop/nominal/v1/data.root)
|   |   |     -> absent
```

Note that parameters such as `version` and `dataset` are passed from `SelectAndReconstruct` to `ConvertData` and `FetchData`. This kind of *soft information* can be set on task level with fine granularity.

Let's run the tasks (**make sure the docker daemon is running**):

```bash
$ law run singletop.SelectAndReconstruct --version v1 --dataset singleTop --local-scheduler
```

It might take a few moments for the tasks to start, because a docker image is downloaded in the background which is required by two of the three tasks. You can transparently use, update, or remove that image afterwards.

The two tasks use additional software (numpy and ROOT) which wasn't installed in the setup section above. However, they make use of law's sandboxing mechanism which builds up the tree in the current environment, but forwards parts of its execution (i.e., the tasks' `run` methods) to different environments. Currently, law supports docker and singularity containers, as well as plain subshells with custom init files (e.g. for sourcing special software (CMSSW...) and setting variables).

Once the tasks are done, you can run the full analysis to obtain the result plots.

```bash
$ law run singletop.CreateHistograms --version v1 --local-scheduler
```

Feel free to check the status again before the actual task processing.

The task graph will look like this:

![example graph](https://www.dropbox.com/s/9jjezagvyfpph9f/st_graph.png?raw=1)

This might take a few minutes. If you want to use multiple CPU cores (say 4), add `--workers 4`. If you use the central scheduler and forgot to set the number of workers, you can conveniently adjust that number right from your browser.

Finally, unpack the output archive and watch the histograms you created!


### Resources

- [law](https://github.com/riga/law)
- [luigi](http://luigi.readthedocs.io/en/stable)
- [CMS Open Data](http://opendata.cern.ch/research/CMS)
- LHC / CMS resources:
  - [Recorded luminosity](https://twiki.cern.ch/twiki/bin/view/CMSPublic/DataQuality#2011_Proton_Proton_Collisions)


### Authors

- [Marcel R.](https://github.com/riga)


### License

The MIT License (MIT)

Copyright (c) 2018 Marcel R.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
