# OD1NF1ST
MIL-STD-1553 Avionic Platform Intrusion Detection System

<img width="1798" alt="image" src="https://user-images.githubusercontent.com/8474647/141875466-435a039b-0d23-4e84-90fb-d9ac299fa2ea.png">



### Source listing

```
.
├── docs                documentations/references
├── odf                 the main simulation/IDS package
│   ├── dependencies    other dependencies such as elasticsearch
│   ├── ids             intrusion detection module
│   ├── mfs             subsystem (sensor/gauge-level) simulation
│   ├── sabotage        implemented attacks
│   └── web             web-based application UI (compiled JavaScript)
├── odf_data            data folder
│   ├── dump            data dumps for training/evaluation purpose
│   ├── models          saved models
│   ├── scene-1         scenario #1 to be used in the simulation
│   ├── scene-2         scenario #2 to be used in the simulation
│   ├── scene-3         scenario #3 to be used in the simulation
├── odf_test            testing code
├── odf_ui              web-based application UI (JavaScript before compilation)
└── solution_systems    web-based application UI (Source code used for experiments)

```


### Running the full simulation system:
```
Requirement: any OS with python3.7+

1/ install/update dependencies
pip install -r requirements.txt


2/ run the system:
# The landing page will automatically pop up in the browser.
# If not, one can access the landing page at: http://127.0.0.1:8572/
python -m odf.web

```

### Running the full simulation system (through Docker):

```
docker build -t l1nna/od1nf1st:v0.0.1 .

# foreground run
docker run -p 8572:8572  l1nna/od1nf1st:v0.0.1

# background run:
docker run -d -p 8572:8572  l1nna/od1nf1st:v0.0.1


```


### Running other subsystems for testing purpose:
```
# install dependencies
pip install -r requirements.txt

# bus system simulation
export SYS_LOG_EVENT=True && python -m odf

# sensor system simulation
# SYS_LOG_EVENT value will be mapped to config object in config.py
export SYS_LOG_EVENT=False && python -m odf.mfs
```

