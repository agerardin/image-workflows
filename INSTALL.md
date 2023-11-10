 # create conda environment 
 # (necessary on osx as we need to build Filepattern2)

 ```
 conda create -n viz-workflow python=3.9
 conda activate viz-workflow
```

# install poetry
```
conda install -c conda-forge poetry
```

# install dependencies

```
poetry install
```

# install wic dependencies
conda env update --file wic_dependencies.yml

