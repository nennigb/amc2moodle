#!/bin/bash

## script to run amc2moodle or moodle2amc automatically in a specific folder

# monitored and daemon folder
MONITOR_DIR_DEF=/tmp/work
LOG_DIR_DEF=/tmp/daemon
#
if [ -z ${MONITOR_DIR+x} ]
then 
    MONITOR_DIR=${MONITOR_DIR_DEF}
fi
if [ -z ${LOG_DIR+x} ]
then 
    LOG_DIR=${LOG_DIR_DEF}
fi

# function to run amc2moodle
function run_amc2moodle()
{
    amc2moodle -x --silent "$1"
    touch "$1".lock
}

# function to run moodle2amc
function run_moodle2amc()
{
    moodle2amc --silent "$1"
    touch "$1".lock
}


#log manage
now=$(date +"%Y-%m-%d_%H-%M-%s")
mkdir -p ${LOG_DIR}
LOGFILE=${LOG_DIR}/${now}_autorun.log

{

printf "Start daemon\n\n"
printf "Log dir: ${LOG_DIR}\n"
printf "Monitored dir: ${MONITOR_DIR}\n"
# loop
while true
do
    #execute on amc2moodle waiting files
    files=$(ls *amc2moodle.tex 2> /dev/null)
    nbfiles=$(ls *amc2moodle.tex 2> /dev/null | wc -l)
    if [ "$nbfiles" != "0" ]
    then
        for file in ${files}
        do
            if [[ -f "${file}.lock" ]]
            then
                printf " >>> ${file}.lock exists\n"
            else
                printf " >>> Run amc2moodle on ${file}\n"
                run_amc2moodle "${file}"
            fi
        done
    fi
    
    #execute on moodle2amc waiting files
    files=$(ls *moodle2amc.xml 2> /dev/null)
    nbfiles=$(ls *moodle2amc.xml 2> /dev/null | wc -l)
    if [ "$nbfiles" != "0" ]
    then
        for file in ${files}
        do
            if [[ -f "${file}.lock" ]]
            then
                printf " >>> ${file}.lock exists\n"
            else
                printf " >>> Run moodle2amc on ${file}\n"
                run_moodle2amc "${file}"
            fi
        done
    fi
    sleep 2
done
printf "Daemon stopped"


} 2>&1 | tee ${LOGFILE}
