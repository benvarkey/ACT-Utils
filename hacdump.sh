#!/bin/bash

_dump_dot_(){
    # $1: name of the hackt object file
    # $2: name of the output dot file
    # $3: type of simulation
    SIMTOOL=""
    if [[ $4 == "chp" ]];
    then
        hacchpsim -fdump-dot-struct -fshow-channels -fshow-event-index -fno-run $1 > $2
        sed -i .bak -Ee s/\[[0-9]+\]\ pid=[0-9]+\\\\n/\ /g -e s/\[[0-9]+\]\ pid=[0-9]/\ /g $2
        rm $2.bak
    elif [[ $4 == "prs" ]];
    then
        hacprsim -fdump-dot-struct -fno-run $1 > $2
    fi
}

_dump_trace_(){
    # $1: name of the hackt object file
    # $2: name of the trace file
    # $3: name of the output trace-dump text file
    # $4: type of simulation

    SIMTOOL=""
    if [[ $4 == "chp" ]];
    then
        SIMTOOL=hacchpsim
    elif [[ $4 == "prs" ]];
    then
        SIMTOOL=hacprsim
    fi
    (echo "trace-dump $2" | $SIMTOOL -b $1) > $3.full_trace
    hacobjdump -a -G $1 > $3.full_map
    if [[ $4 == "chp" ]];
    then
        (awk '/bool state trace:/ {exit} {print}' $3.full_trace | sed -Ene '/^([[:space:]]+[[:digit:]]+){4}$/p') > $3.events
        (awk '/bool state trace:/,/int state trace:/' $3.full_trace | sed -Ene '/^([[:space:]]+[[:digit:]]+){3}$/p') > $3.states
    fi
    if [[ $4 == "prs" ]];
    then
        (awk '/^Epoch/,0' $3.full_trace | sed -Ene '/^([[:space:]]+[[:graph:]]+){7}/p' | sed -Ee 's/X/NaN/') > $3.events
    fi
    (awk '/\[global bool/,0{if (!/\[global bool/) print}' $3.full_map | awk '/^\[/ || 0 {exit} {print}' | sed -nEe '/^([[:graph:]]+[[:space:]]+){5}$/p' | sed -Ee 's/([[:space:]]+[[:graph:]]+){3}//') > $3.map
}

_print_usage_(){
    cat << EOF
    usage: $0 <OPTIONS> <HACKT compiled file>

    This script reads in a HACKT compiled file and dumps out
    a DOT file or a text dump of binary trace file.

    OPTIONS:
        -d  Output DOT filename
        -t  Output text dump for binary trace [use with -b]
        -b  Input binary trace file [use with -t]
        -s  Type of simulator ('chp' or 'prs')
EOF
exit 1
}

TRACE_IN=""
TRACE_OUT=""
HAC_IN=""
DOT_OUT=""
SIM_TYPE=""

while getopts "d:b:t:s:h" flag
do
    case $flag in
        b) TRACE_IN=$OPTARG
            ;;
        t) TRACE_OUT=$OPTARG
            ;;
        d) DOT_OUT=$OPTARG
            ;;
        s) SIM_TYPE=$OPTARG
            ;;
        h) _print_usage_
            ;;
        \?) echo "Invalid option: -$OPTARG"
            _print_usage_
            ;;
        :) echo "Option -$OPTARG requires an argument"
            _print_usage_
            ;;
    esac
done

shift $((OPTIND-1))
HAC_IN=$1

if [[ -z $HAC_IN ]]; then
    echo "HACKT compiled object file not specified"
    _print_usage_
fi

if [[ $TRACE_IN || $TRACE_OUT ]]; then
    if [[ (-z $TRACE_IN) || (-z $TRACE_OUT) ]]; then
        echo "-b and -t should be used together"
        echo ""
        _print_usage_
    else
        _dump_trace_ $HAC_IN $TRACE_IN $TRACE_OUT $SIM_TYPE
    fi
fi

if [[ $DOT_OUT ]]; then
    _dump_dot_ $HAC_IN $DOT_OUT $SIM_TYPE
fi
