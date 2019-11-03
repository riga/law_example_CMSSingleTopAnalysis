![law](https://raw.githubusercontent.com/riga/law/master/logo.png)

# SingleTop Analysis with Public CMS Data using *law*


This exampl uses CMS OpenData (2011) to perform a very simple single-top quark analysis. Its output is a set of histograms of kinematic distributions after performing simplistic selection and reconstruction algorithms. The example is desined to showcase the [**luigi analysis workflow**](https://github.com/riga/law) (law) package.


### Getting started

To get familiar with law, have a look at these simple examples:

- [loremipsum](https://github.com/riga/law/tree/master/examples/loremipsum) (measuring character frequencies)
- [htcondor_at_cern](https://github.com/riga/law/tree/master/examples/htcondor_at_cern) (workflows that submit tasks via HTCondor)


### Requirements

The tasks in this example analysis require docker to be installed on your system. Other dependencies are conveniently installed (**once**) when you source the setup script,

```shell
source setup.sh
```

This will create a directory `tmp/software` at the top level directory of the repository with five required python packages ([luigi](https://github.com/spotify/luigi), [six](https://github.com/benjaminp/six), [scinum](https://github.com/riga/scinum), [law](https://github.com/riga/law), and [order](https://github.com/riga/order)).


### Setup

If you haven't done so already, simply run

```shell
source setup.sh
```

and you are good to go.

If you want to see the tasks' dependency tree and progress live in your browser, open a second shell, source the setup script again and start a central luigi scheduler,

```shell
luigid
```

If you decided to use the central scheduler, you can remove the `local_scheduler` option in the `[luigi_core]` section of the `law.cfg` configuration file.


### Running the Analysis

The analysis configuration is placed in [analysis/framework](analysis/framework) (too big a word for what it actually is). It contains a stack plotting method, and the implementation of selection, reconstruction and systematics. Those are not designed to be very performant - their purpose is to show event-by-event processing within law tasks. Although backed by numpy arrays, the processing is not numpy-vectorized for the sake of using simple TLorentzVector's (see e.g. [coffea](https://github.com/CoffeaTeam/coffea) for more info on columnar analysis).

The [analysis/config](analysis/config) directory contains the definition of input datasets, physics processes and constants, cross sections, and generic analysis information using the [order](https://github.com/riga/order) package. Especially processes and datasets could be candidates for public bookkeeping of LHC experiment data.

The actual analysis is defined in [analysis/tasks/simple.py](analysis/tasks/simple.py). The tasks in this file rely on some base classes (`AnalysisTask`, `ConfigTask`, `ShiftTask`, and `DatasetTask`, see [analysis/framework/tasks.py](analysis/framework/tasks.py)), which are defined along the major objects provided by [order](https://github.com/riga/order).


#### Step 0: Let law scan your the tasks and their parameters

You **want** your analysis workflow tool to provide auto-completion for your tasks and their parameters, and so does law. For that purpose, law needs a (human-readable) *index* file, which is faster to *grep* than starting a python interpreter every time you hit `<tab>` to check matching values.

Create the index file:

```shell
> law index --verbose
loading tasks from 1 module(s)
loading module 'analysis.tasks.simple', done

module 'analysis.tasks.simple', 5 task(s):
    - singletop.CreateHistograms
    - singletop.FetchData
    - singletop.ConvertData
    - singletop.VaryJER
    - singletop.SelectAndReconstruct

written 5 task(s) to index file '/law_example_CMSSingleTopAnalysis/.law/index'
```

In general, law could also work without the *index* file, but it's very convenient to have it.


#### Step 1: Fetch a CMS OpenData file

```shell
law run singletop.FetchData --version v1 --dataset singleTop
```

This will download a file from the CERN OpenData portal and store it locally on your computer. The exact location is defined on task level and (e.g.) can be printed from the command line by checking the status of the task:


```shell
> law run singletop.FetchData --version v1 --dataset singleTop --print-status 0
print task status with max_depth 0 and target_depth 0

check status of singletop.FetchData(version=v1, effective_shift=nominal, dataset=singleTop)
|   - LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/tmp/data/singletop.FetchData/singletop_opendata_2011/singleTop/nominal/v1/data.root)
|     -> existent
```

From the status text of the previous command you see that the output file exists. The path of the `LocalFileTarget` is quite long, which is not particularly law-specific but rather subject to the base task classes in this example which define how *significant* task parameters are encoded in output target paths. However, in reality, one shouldn't care too much about the exact paths, as long as task parameters are encoded consistently.

**Note**:

  - The `--version` parameter is encoded into the output directory. The exact behavior can be controller per task. See the base task definitions in [analysis/framework/tasks.py](analysis/framework/tasks.py) for more info. Those tasks are not shipped with law itself, but they are provided by this example as some kind of *minimal framework*.
  - The value passed to the `--dataset` parameter is used by the `DatasetTask` base task (i.e. all tasks in this example that treat a particular dataset, see the previous link) to match against an `order.Dataset` object defined in [analysis/config/opendata_2011.py](analysis/config/opendata_2011.py). This configuration file contains and describes all CMS OpenData files used in this example. It is actually independent of any analysis and could also be provided centrally. Click [here](https://github.com/riga/order) for more info on the `order` package.


#### Step 2: Exercise: Delete the output again

```shell
> law run singletop.FetchData --version v1 --dataset singleTop --remove-output 0
remove task output with max_depth 0
removal mode? [i*(interactive), a(all), d(dry)] # type 'a'

selected all mode

remove output of singletop.FetchData(version=v1, effective_shift=nominal, dataset=singleTop)
|   - LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop.FetchData/singletop_opendata_2011/singleTop/nominal/v1/data.root)
|     removed
```

(`--remove-output 0,a` would have get you to the same result without getting the prompt)

The number passed to both `--print-status` and `--remove-output` is the tree depth. 0 refers to the task defined in `law run` itself, 1 refers to the first level of dependencies, etc, and negative numbers result in full recursion (handle with care).

When running output removal in interactive mode, you are asked for every single output target whether you want to remove it or not.


#### Step 3: Check the workflow structure (up to selection and reconstruction)

First, check the status of the `SelectAndReconstruct` task to get an idea of that the command will execute:

```shell
> law run singletop.SelectAndReconstruct --version v1 --dataset singleTop --print-status -1
print task status with max_depth -1 and target_depth 0

check status of singletop.SelectAndReconstruct(version=v1, effective_shift=nominal, dataset=singleTop)
|   - LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop.SelectAndReconstruct/singletop_opendata_2011/singleTop/nominal/v1/data.npz)
|     -> absent
|
|   > status of singletop.ConvertData(version=v1, effective_shift=nominal, dataset=singleTop)
|   |   - check LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop.ConvertData/singletop_opendata_2011/singleTop/nominal/v1/data.npz)
|   |     -> absent
|   |
|   |   > status of singletop.FetchData(version=v1, effective_shift=nominal, dataset=singleTop)
|   |   |   - check LocalFileTarget(path=/law_example_CMSSingleTopAnalysis/data/singletop.FetchData/singletop_opendata_2011/singleTop/nominal/v1/data.root)
|   |   |     -> absent
```

Note that the values of the parameters `--version` and `--dataset` are passed from `SelectAndReconstruct` to `ConvertData` and `FetchData`. This kind of *soft information* can be set on task level with fine granularity. When defining requirements to other tasks with the same parameters, it makes sense to propagate them consistently **or** to explicitely use different values to suite you particular worklfow.


#### Step 4: Run selection and reconstruction

For that, **make sure the docker daemon is running**. Then run:

```shell
law run singletop.SelectAndReconstruct --version v1 --dataset singleTop
```

It might take a few moments for the tasks to start, because a docker image is downloaded in the background which is required by two of the three tasks. You can transparently use, update, or remove that image afterwards. The containers created from this image are removed upon tasks success automatically.

The two tasks use additional software (numpy and ROOT) which wasn't installed in the setup section above. However, they make use of law's sandboxing mechanism which builds up the tree in the current environment, but forwards parts of its execution (i.e., the task's `run()` method) to different environments. Currently, law supports docker and singularity containers, as well as plain bash subshells with custom initialization files (e.g. for sourcing special software (CMSSW, ...) and variables).

When the tasks succeed, look into the target directories to see their outputs. You can also run the above command extended by `--print-status -1` again.


#### Step 5: Run the full analysis to get histograms

The tasks above fetched data, converted them to numpy arrays, and performed a basic selection and reconstruction for the `singleTop` dataset only.

For the other datasets considered in this example (see what is defined in [analysis/config/singletop.py](analysis/config/singletop.py)), you could run the same `law run singletop.SelectAndReconstruct --dataset ...` command. But as we are interested in some histograms of kinematic distributions, we can just run the particular plotting task, which will automatically trigger all required tasks that are not complete yet (i.e. tasks whose outputs do not exist yet):

```shell
law run singletop.CreateHistograms --version v1
```

Feel free to check the status again before the actual task processing by appending `--print-status -1`.

**Also** you might want to increase the number of parallel processes for this command. To do so, add `--workers N` and luigi will handle the process scheduling for you.

In case you are using a central luigi scheduler to visualize dependency trees and live task status, you will see a graph like this:

![example graph](https://www.dropbox.com/s/9jjezagvyfpph9f/st_graph.png?raw=1)

The processing might take a few minutes.

Finally, unpack the output archive and watch the histograms you created!


### Resources

- [law](https://github.com/riga/law)
- [luigi](http://luigi.readthedocs.io/en/stable)
- [order](https://github.com/riga/order)
- [CMS Open Data](http://opendata.cern.ch/research/CMS)
- LHC / CMS resources:
    - [Recorded luminosity](https://twiki.cern.ch/twiki/bin/view/CMSPublic/DataQuality#2011_Proton_Proton_Collisions)
