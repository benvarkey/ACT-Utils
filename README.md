#ACT-Utils : Utilities for [H]AC[K]T

The utilities currently work only with Fang's HACKT suite. The tools assume that you have HACKT tools (_hacchpsim_, _hacprsim_ etc.) in path.

## hacdump.sh
This utility generates a DOT file for HACKT processes and a text dump from the simulation results, both of which are needed for _ACT.Inspect_ Python module.

First, generate a compiled HACKT file &lt;_process.hacc_&gt;, from your _.hac_ source code &lt;_input.hac_&gt;:
```
sh> haco <input.hac> <intermediate.haco>
sh> haccreate <intermediate.haco> <process.hacc>
```

Launch _hacchpsim_ or _hacprsim_:

```
sh> hacchpsim <process.hacc>
```

Once you have initialized all the variables and before you run the simulation (using ```run``` or ```advance``` commands), use
```
chpsim> trace <traces.bin>
``` 
to initialize a trace-dump file. When you are done with the simulation, do
```
chpsim> trace-close
```
to save the simulations to the trace file and close it.

Once you have the &lt;_process.hacc_&gt; and &lt;_traces.bin_&gt; file, you can use _hacdump.sh_:
```
sh> ./hacdump.sh -d <process.dot> -t <traces.out> -b <traces.bin> -s <chp,prs> <process.hacc>
```
which should create the following files:

* **&lt;_process.dot&gt;_** (for **chp/hse** only): DOT file showing process hierarchy.
* **&lt;_traces.out.map&gt;_**: mapping between global variables and their unique identifiers.
* **&lt;_traces.out.events&gt;_**: text dump of event times and process-event at the times.
* **&lt;_traces.out.states&gt;_** (for **chp/hse** only): text dump of event indices and process-state at the event.
* **&lt;_traces.out.full_map&gt;_**: complete mapping between global/local variables and their unique identifiers.
* **&lt;_traces.out.full_trace&gt;_**: complete text dump of &lt;_traces.bin_&gt;.

```./hacdump.sh -h``` prints the usage.

## ACT.Inspect
This Python module visualizes the simulation dumps created by _hacdump.sh_. 


To use it, launch a Python shell and:
```python
import ACT.Inspect as insp

insp.ShowStateTransition('<process.dot>', '<traces.out.events>', '<traces.out.states>', '<traces.out.map>')
```

Right now, the module works only with HSE simulations.
![Sample frame from animation](./images/ACT_Inspect_static_demo.png?raw=true "ACT.Inspect.ShowStateTransition() output")

During the visualization, latest event node is highlighted with the darkest green. As events progress (and time as well), nodes that are not visited fade away. The number inside a node tells how many times that event has occured.
The states of various variables (wires) at the latest event is shown at the bottom.
