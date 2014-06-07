#!/bin/bash

_dump_dot_(){
    # $1: name of the hackt object file
    # $2: name of the output dot file
    hacchpsim -fdump-dot-struct -fshow-channels -fshow-event-index -fno-run $1 > $2
    sed -i .bak -Ee s/\[[0-9]+\]\ pid=[0-9]+\\\\n/\ /g -e s/\[[0-9]+\]\ pid=[0-9]/\ /g $2
    rm $2.bak
}

_dump_trace_(){
    # $1: name of the hackt object file
    # $2: name of the trace file
    # $3: name of the output trace-dump text file

    (echo "trace-dump $2" | hacchpsim -b $1) > $3.bak
    (awk '/bool state trace:/ {exit} {print}' $3.bak | sed -Ene '/^([[:space:]]+[[:digit:]]+){4}$/p') > $3
    rm $3.bak
}

_print_usage_(){
    cat << EOF
    usage: $0 <OPTIONS> <HACKT compiled file>

    This script reads in a HACKT compiled file
    and dumps out a DOT file or a text dump of
    binary trace file.

    OPTIONS:
        -d  Output DOT filename
        -t  Output text dump for binary trace [with -b]
        -b  Input binary trace file [with -t]
EOF
exit 1
}

TRACE_IN=""
TRACE_OUT=""
HAC_IN=""
DOT_OUT=""

while getopts "d:b:t:" flag
do
    case $flag in
        b) TRACE_IN=$OPTARG
            ;;
        t) TRACE_OUT=$OPTARG
            ;;
        d) DOT_OUT=$OPTARG
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
        _dump_trace_ $HAC_IN $TRACE_IN $TRACE_OUT
    fi
fi

if [[ $DOT_OUT ]]; then
    _dump_dot_ $HAC_IN $DOT_OUT
fi
