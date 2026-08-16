#!/usr/bin/env julia

using ArgParse
using JSON3
using ThesisCLI

function parse_args()
    settings = ArgParseSettings()

    @add_arg_table settings begin
        "command"
            help = "Command: scan or packet"
            required = true
        "path"
            help = "Path to scan"
            required = true
        "--out"
            help = "Output directory"
            default = "thesis_packet"
    end

    return ArgParse.parse_args(settings)
end

args = parse_args()

if args["command"] == "scan"
    scan = scan_path(args["path"])
    JSON3.pretty(stdout, scan)
    println()
elseif args["command"] == "packet"
    write_packet(args["path"], args["out"])
    println("THESIS packet written to $(args["out"])")
else
    error("Unknown command: $(args["command"])")
end
