# Example configs
Examples here are for a deep learning pipeline.
Each class has a dataclass that holds all the configurations for a certain class.
To change a config from a standard attribute to an Arg that is visible the Argparser, change the default into the corresponding `Arg` type as in the example.
<img alt="The main configuration for the project (MainConf) consists of several sub ArgsGroup" src="mainconf_tree.png" title="MainConf ArgsGroup tree visualization"/>

## Configs organization
While all the configs are placed in 1 folder here, when integrating this repo to your code, the config files 
can be placed near the corresponding classes for ease of management.

