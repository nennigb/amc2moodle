# Docker's version of `amc2moodle`

A docker version of `amc2moodle` is available and it start a daemon server to automatically execute `amc2moodle` or `moodle2amc`.

# Installation

The container can be downloaded using the following command 
```
docker pull ghcr.io/luclaurent/amc2moodle:latest
```

The container proposes to mount two volumes:
    - `/tmp/work` (**mandatory mount**) that must be link to a specific folder on the host computer
    - `/tmp/daemon` (optional mount) that store the log file of the daemon

For instance, the container can be run in CLI with the following command:
```
docker run --name amc2moodle -d -v "DIRA:/tmp/work" -v "DIRB:/tmp/daemon" ghcr.io/luclaurent/amc2moodle
```

NB: that `DIRA` and `DIRB` must be absolute paths.

** it is recommended to use only empty folder with no critical contents for `DIRA`and `DIRB`. **
# Usage

We assume that `DIRA` has been mounted and bound to `/tmp/work`.

Folder `DIRA` can be populated with every required data to run `amc2moodle` or `moodle2amc` such as
```
DIRA
├── ...
├── a_amc2moodle.tex
├── b_moodle2amc.xml
└── ...
```

The server will automatically detects the files and run the appropriate script:
  - to run `amc2moodle` the main LaTeX file must be rename such as the end the name ends with `amc2moodle.tex` (such as the file `a_amc2moodle.tex`)
  - to run `moodle2amc` the main LaTeX file must be rename such as the end the name ends with `moodle2amc.xml` (such as the file `b_moodle2amc.xml`)

After the run, the folder will contain additional files provided by the daemon/server and the script:

```
DIRA
├── ...
├── a_amc2moodle.tex
├── a_amc2moodle.tex.lock
├── a_amc2moodle_amc2moodle.log
├── b_moodle2amc.xml
├── b_moodle2amc.xml.lock
├── b_moodle2amc_moodle2amc.log
└── ...
```

Logfiles (`*.log`) are provided by the `amc2moodle`or `moodle2amc` scripts and allows to check if everything is fine.

Lockfiles (`*.lock`) are provided by the daemon/server. **Running a new execution could be obtain by removing one of this files.**

In addition, if the `DIRB` directory has been mounted, it will contain detailed logfiles of the daemon and could be use for debug.

<!---
 # Development 
 --->

