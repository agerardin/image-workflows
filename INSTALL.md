 # create conda environment 
 # (necessary on osx as we need to build Filepattern2)

 ```
 conda create -n viz-workflow python=3.9
 conda activate viz-workflow
```

# installing poetry
```
conda install -c conda-forge poetry
```

# installing polus-plugins
poetry add git+https://github.com/PolusAI/polus-plugins

# installing Camilo's fork of wic (including the wic api)
poetry add git+https://github.com/camilovelezr/workflow-inference-compiler.git@viz

# installing wic dependencies
conda env update --file wic_dependencies.yml

