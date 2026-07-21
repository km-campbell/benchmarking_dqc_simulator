# Profiling for dqc_simulator

Profiling of the [dqc_simulator](https://github.com/km-campbell/dqc_simulator.git) package.

The main branch contains code for profiling using the density matrix formalism. The other_formalisms branch runs the profiling code with the stabiliser formalism. This is clearly not the most elegant or maintainable way of having two different formalisms but it gets the job done and kept development time manageable, which was necessary here and should be sufficient for these purposes. If more profiling needs to be added to in the future then refactoring will be done then.

To reproduce the results, the code should be run inside the included uv environment using `uv run <script name>`. The setup.py script contains the code to be profiled and some helper functions. memory_benchmarks.py and time_benchmarks.py takes results for memory and time respectively and plots.py plots those results. The filepaths to save to and import from should be updated in those three scripts to reflect where the data should be stored.